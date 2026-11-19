mod db;
mod proxy;
mod ws;

use anyhow::{Context, Result};
use axum::{
    body::Body,
    extract::{Path, Query, Request, WebSocketUpgrade},
    http::StatusCode,
    response::{IntoResponse, Redirect, Response},
    routing::get,
    Extension, Router,
};
use axum_extra::extract::cookie::{Cookie, CookieJar};
use chrono::Utc;
use hyper_util::{client::legacy::connect::HttpConnector, rt::TokioExecutor};
use jsonwebtoken::{decode, encode, Algorithm, DecodingKey, EncodingKey, Validation};
use lazy_static::lazy_static;
use serde::{Deserialize, Serialize};
use sqlx::{mysql::MySqlPoolOptions, MySqlPool};
use std::time::Duration;
use std::{env::var, sync::Arc};
use tower_http::trace::{self, TraceLayer};
use tracing::Level;

const PROXY_SERVER_PORT: u64 = 5000;
// TODO: add back port range
// const MAX_PROXY_PORT: u64 = 8010;
const MAX_DB_CONNECTIONS: u32 = 50;
const FAILED_REDIRECT_URL: &str = "https://anubis-lms.io/error";
const JWT_EXPIRATION_HOURS: i64 = 6;

// Lazy static evaluation of environment variables
lazy_static! {
    static ref IS_DEBUG: bool = {
        match var("DEBUG").unwrap_or("false".to_string()).parse() {
            Ok(val) => val,
            Err(_) => false,
        }
    };
    static ref SECRET_KEY: String = {
        match var("SECRET_KEY") {
            Ok(key) => key,
            Err(_) => "DEBUG".to_string(),
        }
    };
    static ref DB_URL: String = {
        let host = var("DB_HOST").unwrap_or("127.0.0.1".to_string());
        let port = var("DB_PORT").unwrap_or("3306".to_string());
        let user = String::from("anubis");
        let database = String::from("anubis");
        let password = var("DB_PASSWORD").unwrap_or("anubis".to_string());

        format!(
            "mysql://{}:{}@{}:{}/{}",
            user, password, host, port, database
        )
    };
}

pub type Client = hyper_util::client::legacy::Client<HttpConnector, Body>;

#[derive(Debug, Serialize, Deserialize)]
struct Claims {
    exp: usize,
    session_id: String,
    #[serde(rename = "netid")]
    net_id: String,
}

fn authenticate_jwt(token: &str) -> Result<Claims> {
    let key: DecodingKey = DecodingKey::from_secret((*SECRET_KEY).as_bytes());
    let validation = Validation::new(Algorithm::HS256);
    let decoded = decode::<Claims>(token, &key, &validation)?;

    Ok(decoded.claims)
}

fn create_jwt(session_id: &str, net_id: &str) -> Result<String> {
    let key = EncodingKey::from_secret(SECRET_KEY.as_bytes());

    let expiration = Utc::now()
        .checked_add_signed(chrono::Duration::hours(JWT_EXPIRATION_HOURS))
        .expect("valid timestamp")
        .timestamp();

    let claims = Claims {
        exp: expiration as usize,
        session_id: session_id.to_string(),
        net_id: net_id.to_string(),
    };

    let token = encode(&jsonwebtoken::Header::default(), &claims, &key)?;

    Ok(token)
}

async fn ping(jar: CookieJar, Extension(pool): Extension<Arc<MySqlPool>>) -> (StatusCode, String) {
    // Asynchronously update the last proxy time for the session
    // if the request contains a valid ide jwt cookie
    if let Some(cookie) = jar.get("ide") {
        authenticate_jwt(cookie.value()).ok().map(|claims| {
            tokio::spawn(async move {
                let result = db::update_last_proxy_time(&claims.session_id, &pool).await;
                if let Err(e) = result {
                    tracing::error!("failed to update last proxy time: {}", e);
                }
            });
        });
    }

    (StatusCode::OK, "pong".to_string())
}

#[derive(Deserialize)]
struct InitializeQueryParams {
    token: String,
}

async fn initialize(params: Query<InitializeQueryParams>, jar: CookieJar) -> impl IntoResponse {
    let failed_response = {
        (
            StatusCode::PERMANENT_REDIRECT,
            jar.clone(),
            Redirect::to(FAILED_REDIRECT_URL),
        )
    };

    let token = match authenticate_jwt(&params.token) {
        Ok(claims) => claims,
        Err(err) => {
            tracing::error!("failed to authenticate jwt: {}", err);
            return failed_response;
        }
    };

    let new_token = create_jwt(&token.session_id, &token.net_id).unwrap();
    let ide_cookie = Cookie::new("ide", new_token);
    let new_jar = jar.add(ide_cookie);

    (
        StatusCode::PERMANENT_REDIRECT,
        new_jar,
        Redirect::to("/ide/"),
    )
}

#[derive(Debug)]
pub struct Target {
    pub host: String,
    pub port: u16,
}

#[derive(Debug)]
enum ProxyType {
    Http,
    WebSocket,
}

/// Handles generic incoming requests to be proxied to the coder server
/// Depending on wether the upgrade websocket header is present
/// the request will be proxied as a websocket or http request
async fn handle(
    ws_upgrade: Option<WebSocketUpgrade>,
    Extension(pool): Extension<Arc<MySqlPool>>,
    Extension(client): Extension<Arc<Client>>,
    _path: Option<Path<String>>,
    jar: CookieJar,
    req: Request,
) -> Result<Response, (StatusCode, String)> {
    let proxy_type = match ws_upgrade {
        Some(_) => ProxyType::WebSocket,
        None => ProxyType::Http,
    };

    let token = match jar.get("ide") {
        Some(cookie) => match authenticate_jwt(cookie.value()) {
            Ok(claims) => claims,
            Err(err) => {
                tracing::error!("failed to authenticate jwt: {}", err);
                return Err((StatusCode::UNAUTHORIZED, "Invalid token".to_string()));
            }
        },
        None => {
            tracing::error!("could not find jwt");
            return Err((StatusCode::UNAUTHORIZED, "No token provided".to_string()));
        }
    };

    let cluster_address = db::get_cluster_address(&pool, &token.session_id)
        .await
        .map_err(|e| {
            tracing::error!("failed to get cluster address: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                "Internal server error".to_string(),
            )
        })?;

    let target = Target {
        host: cluster_address.clone(),
        // TODO: handle port from the request path
        port: 5000,
    };

    tracing::debug!("proxying request to target: {:?}", target);

    let result = match proxy_type {
        ProxyType::Http => match proxy::proxy_req(client, req, target).await {
            Ok(res) => res,
            Err(err) => {
                tracing::error!("failed to proxy http request: {}", err);
                return Err((
                    StatusCode::INTERNAL_SERVER_ERROR,
                    "failed to proxy http request".to_string(),
                ));
            }
        },
        ProxyType::WebSocket => {
            if let Some(ws) = ws_upgrade {
                // upgrade the connection to websocket and proxy the websocket request to the
                // target host and port
                ws.on_upgrade(move |socket| ws::forward(socket, target))
            } else {
                return Err((
                    StatusCode::BAD_REQUEST,
                    "no ws upgrade found for ws proxy request".to_string(),
                ));
            }
        }
    };

    Ok(result)
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_target(false)
        .compact()
        .init();

    let pool = Arc::new(
        MySqlPoolOptions::new()
            .max_connections(MAX_DB_CONNECTIONS)
            .acquire_timeout(Duration::from_secs(5))
            .connect(&DB_URL)
            .await
            .context("failed to connect to db")?,
    );

    // client used for proxying http requests
    let client: Arc<Client> = Arc::new(
        hyper_util::client::legacy::Client::<(), ()>::builder(TokioExecutor::new())
            .build(HttpConnector::new()),
    );

    let app = Router::new()
        .route("/ping", get(ping))
        .route("/initialize", get(initialize))
        // Seems like we need to handle `/` and `/*` seperately ?
        .route("/", get(handle))
        .route("/*path", get(handle))
        .layer(Extension(pool))
        .layer(Extension(client))
        .layer(
            TraceLayer::new_for_http()
                .make_span_with(trace::DefaultMakeSpan::new().level(Level::INFO))
                .make_span_with(trace::DefaultMakeSpan::new().level(Level::INFO))
                .on_failure(trace::DefaultOnFailure::new().level(Level::ERROR))
                .on_request(trace::DefaultOnRequest::new().level(Level::INFO))
                .on_response(trace::DefaultOnResponse::new().level(Level::INFO)),
        );

    tracing::info!("server started on port {}", PROXY_SERVER_PORT);
    let listener = tokio::net::TcpListener::bind(format!("0.0.0.0:{}", PROXY_SERVER_PORT))
        .await
        .unwrap();

    axum::serve(listener, app).await.unwrap();

    Ok(())
}
