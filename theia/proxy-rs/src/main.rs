use anyhow::Result;
use axum::{extract::Path, http::StatusCode, response::Redirect, routing::get, Extension, Router};
use axum_extra::extract::cookie::{Cookie, CookieJar};
use jsonwebtoken::{decode, encode, Algorithm, DecodingKey, EncodingKey, Validation};
use lazy_static::lazy_static;
use serde::{Deserialize, Serialize};
use sqlx::{mysql::MySqlPoolOptions, prelude::FromRow, MySqlPool};
use std::{env::var, sync::Arc};


const MAX_PROXY_PORT: u64 = 8010;
const MAX_DB_CONNECTIONS: u32 = 50;
const FAILED_REDIRECT_URL: &str = "https://anubis-lms.io/error";

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

    Ok(decoded.claims)
}

fn create_jwt(session_id: &str, net_id: &str) -> Result<String> {
    let key = EncodingKey::from_secret(SECRET_KEY.as_bytes()); 
    let claims = Claims {
        exp: 1000000000,
        session_id: session_id.to_string(),
        net_id: net_id.to_string(),
    };

    let token = encode(&jsonwebtoken::Header::default(), &claims, &key)?;

    Ok(token)
}

async fn ping() -> (StatusCode, String) {
    (StatusCode::OK, "pong".to_string())
}

async fn initialize(jar: CookieJar) -> (StatusCode, CookieJar, Redirect, String) {
    let failed_response = | reason: &str | {
        return (
            StatusCode::UNAUTHORIZED,
            jar.clone(),
            Redirect::to(&FAILED_REDIRECT_URL),
            reason.to_string()
        );
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
    let new_jar = jar.add(Cookie::new("ide", new_token));

    (
        StatusCode::OK,
        new_jar,
        Redirect::to("https://anubis-lms.io/"),
        "authorized".to_string(),
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
        "#
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
        },
        None => Err(anyhow::anyhow!("Session not found")),
    }
}

async fn handle(Path(path): Path<String>, Extension(pool): Extension<Arc<MySqlPool>>, jar: CookieJar) -> (StatusCode, String) {
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

    let cluster_address = get_cluster_address(&pool, &token.session_id).await.map_err(|e| {
        eprintln!("Error: {}", e);
        (StatusCode::INTERNAL_SERVER_ERROR, "Internal server error".to_string())
    }).unwrap();
    return (StatusCode::OK, "authorized".to_string());
}

#[tokio::main]
async fn main() {
    let pool = MySqlPoolOptions::new()
        .max_connections(MAX_DB_CONNECTIONS)
        .connect(&DB_URL).await.unwrap();


    let pool = Arc::new(pool);

    let app = Router::new()
        .route("/ping", get(ping))
        .route("initialize", get(initialize))
        .route("/handle/:port", get(handle))
        .layer(Extension(pool));


    let listener = tokio::net::TcpListener::bind("0.0.0.0:5000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
