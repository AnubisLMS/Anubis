use axum::{
    extract::Request,
    response::{IntoResponse, Response},
};

use anyhow::Result;
use std::sync::Arc;

use super::{Client, Target};

pub async fn proxy_req(client: Arc<Client>, mut req: Request, target: Target) -> Result<Response> {
    let path = req.uri().path();
    let path_query = req
        .uri()
        .path_and_query()
        .map(|v| v.as_str())
        .unwrap_or(path);

    *req.uri_mut() = format!("http://{}:{}{}", target.host, target.port, path_query)
        .parse()
        .unwrap();

    Ok(client.request(req).await.unwrap().into_response())
}
