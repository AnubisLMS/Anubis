mod ws;

use anyhow::Result;
use axum::{
    body::Body,
    extract::{Path, Request, WebSocketUpgrade},
    http::StatusCode,
    response::{IntoResponse, Redirect, Response},
    routing::get,
    Extension, Router,
};
use axum_extra::extract::cookie::{Cookie, CookieJar};
use hyper::upgrade::Upgraded;
use hyper_util::rt::TokioIo;
use jsonwebtoken::{decode, encode, Algorithm, DecodingKey, EncodingKey, Validation};
use lazy_static::lazy_static;
use serde::{Deserialize, Serialize};
use sqlx::{mysql::MySqlPoolOptions, prelude::FromRow, MySqlPool};
use std::time::Duration;
use std::{env::var, sync::Arc};
use tokio::net::TcpStream;
use tower_http::trace::{self, TraceLayer};
use tracing::Level;

const PROXY_SERVER_PORT: u64 = 5000;
const MAX_PROXY_PORT: u64 = 8010;
const MAX_DB_CONNECTIONS: u32 = 50;
const FAILED_REDIRECT_URL: &str = "https://anubis-lms.io/error";
/// JWT expires in 6 hours
const JWT_EXPIRATION: usize = 6 * 60 * 60;

// Lazy static evaluation of environment variables
lazy_static! {
    static ref DEBUG: bool = var("DEBUG").unwrap_or("false".to_string()).parse().unwrap();
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
        let password = var("DB_PASSWORD").unwrap_or("anubis".to_string());

        format!("mysql://{}:{}@{}:{}", user, password, host, port)
    };
}

#[derive(Debug, Serialize, Deserialize)]
struct Claims {
    exp: usize,
    session_id: String,
    net_id: String,
}

fn authenticate_jwt(token: &str) -> Result<Claims> {
    let key: DecodingKey = DecodingKey::from_secret(SECRET_KEY.as_bytes());
    let validation = Validation::new(Algorithm::HS256);
    let decoded = decode::<Claims>(token, &key, &validation)?;

    if decoded.claims.exp < JWT_EXPIRATION {
        return Err(anyhow::anyhow!("Token expired"));
    }

    Ok(decoded.claims)
}

fn create_jwt(session_id: &str, net_id: &str) -> Result<String> {
    let key = EncodingKey::from_secret(SECRET_KEY.as_bytes());
    let claims = Claims {
        exp: JWT_EXPIRATION,
        session_id: session_id.to_string(),
        net_id: net_id.to_string(),
    };

    let token = encode(&jsonwebtoken::Header::default(), &claims, &key)?;

    Ok(token)
}

async fn update_last_proxy_time(session_id: &str, pool: &MySqlPool) -> Result<()> {
    sqlx::query(
        r#"
        UPDATE theia_session
        SET last_proxy = NOW()
        WHERE id = $1
        "#,
    )
    .bind(session_id)
    .execute(pool)
    .await?;

    Ok(())
}

async fn ping(jar: CookieJar, Extension(pool): Extension<Arc<MySqlPool>>) -> (StatusCode, String) {
    match jar.get("ide") {
        Some(cookie) => match authenticate_jwt(cookie.value()) {
            Ok(claims) => {
                update_last_proxy_time(&claims.session_id, &pool)
                    .await
                    .unwrap();
            }
            Err(_) => {}
        },
        None => {}
    };

    (StatusCode::OK, "pong".to_string())
}

async fn initialize(jar: CookieJar) -> impl IntoResponse {
    let failed_response = |_reason: &str| {
        (
            StatusCode::PERMANENT_REDIRECT,
            jar.clone(),
            Redirect::to(FAILED_REDIRECT_URL),
        )
    };

    let token = match jar.get("ide") {
        Some(cookie) => match authenticate_jwt(cookie.value()) {
            Ok(claims) => claims,
            Err(_) => {
                return failed_response("Invalid token");
            }
        },
        None => {
            return failed_response("No token provided");
        }
    };

    let new_token = create_jwt(&token.session_id, &token.net_id).unwrap();
    let mut ide_cookie = Cookie::new("ide", new_token);
    ide_cookie.set_http_only(true);

    let new_jar = jar.add(ide_cookie);

    (
        StatusCode::PERMANENT_REDIRECT,
        new_jar,
        Redirect::to("https://anubis-lms.io/"),
    )
}

#[derive(Deserialize, Serialize, FromRow)]
struct TheiaSession {
    cluster_address: Option<String>,
}

async fn get_cluster_address(pool: &MySqlPool, session_id: &str) -> Result<String> {
    let row: Option<TheiaSession> = sqlx::query_as(
        r#"
        SELECT cluster_address
        FROM theia_session
        WHERE id = $1 AND active = 1
        "#,
    )
    .bind(session_id)
    .fetch_optional(pool)
    .await?;

    match row {
        Some(session) => {
            if let Some(cluster_address) = session.cluster_address {
                Ok(cluster_address)
            } else {
                Err(anyhow::anyhow!("Cluster address not found"))
            }
        }
        None => Err(anyhow::anyhow!("Session not found")),
    }
}

async fn handle(
    Path(path): Path<String>,
    ws: WebSocketUpgrade,
    Extension(pool): Extension<Arc<MySqlPool>>,
    jar: CookieJar,
    req: Request,
) -> impl IntoResponse {
    let port = path.parse::<u64>().unwrap();

    if port > MAX_PROXY_PORT {
        return (StatusCode::BAD_REQUEST, "Invalid port".to_string());
    }

    let token = match jar.get("ide") {
        Some(cookie) => match authenticate_jwt(cookie.value()) {
            Ok(claims) => claims,
            Err(_) => {
                return (StatusCode::UNAUTHORIZED, "Invalid token".to_string());
            }
        },
        None => {
            return (StatusCode::UNAUTHORIZED, "No token provided".to_string());
        }
    };

    let cluster_address = get_cluster_address(&pool, &token.session_id)
        .await
        .map_err(|e| {
            eprintln!("Error: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                "Internal server error".to_string(),
            )
        })
        .unwrap();

    let host = format!("ws://{}:{}", cluster_address, port);

    ws.on_upgrade(move |socket| ws::forward(&host, ws));
    (StatusCode::OK, "authorized".to_string())
}


#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_target(false)
        .compact()
        .init();

    let pool = MySqlPoolOptions::new()
        .max_connections(MAX_DB_CONNECTIONS)
        .acquire_timeout(Duration::from_secs(5))
        .connect(&DB_URL)
        .await
        .map_err(|e| {
            tracing::error!("Failed to connect to database: {}", e);
            panic!("Failed to connect to database");
        })
        .map(|_| {
            tracing::info!("Connected to database");
        })
        .unwrap();

    let pool = Arc::new(pool);

    let app = Router::new()
        .route("/ping", get(ping))
        .route("/initialize", get(initialize))
        .route("/:port", get(handle))
        .layer(Extension(pool))
        .layer(
            TraceLayer::new_for_http()
                .make_span_with(trace::DefaultMakeSpan::new().level(Level::INFO))
                .make_span_with(trace::DefaultMakeSpan::new().level(Level::INFO))
                .on_failure(trace::DefaultOnFailure::new().level(Level::ERROR))
                .on_request(trace::DefaultOnRequest::new().level(Level::INFO))
                .on_response(trace::DefaultOnResponse::new().level(Level::INFO)),
        );

    tracing::info!("Server started on port {}", PROXY_SERVER_PORT);

    let listener = tokio::net::TcpListener::bind(format!("0.0.0.0:{}", PROXY_SERVER_PORT))
        .await
        .unwrap();
    axum::serve(listener, app).await.unwrap();
}
