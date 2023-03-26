mod proxy;
mod shutdown;

use http::Response;
use tokio;
use tracing;
use tracing_subscriber;
use hudsucker::{async_trait::async_trait, HttpHandler, HttpContext, RequestOrResponse, *};
use hyper::{Body, Request};

#[derive(Clone)]
pub struct MyHandler;

#[async_trait]
impl HttpHandler for MyHandler {
    async fn handle_request(
        &mut self,
        _ctx: &HttpContext,
        req: Request<Body>,
    ) -> RequestOrResponse {
        println!("in {:?}", req);
        // let (parts, body) = req.into_parts();
        // RequestOrResponse::Request(Request::from_parts(parts, Body::from(body)))
        req.into()
    }

    async fn handle_response(&mut self, _ctx: &HttpContext, res: Response<Body>) -> Response<Body> {
        println!("out {:?}", res);
        res
    }
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    println!("i am not insane");
    let proxy = proxy::new();

    if let Err(e) = proxy.with_http_handler(MyHandler).build().start(shutdown::shutdown_sig()).await {
        tracing::error!("error {}", e);
    }
}
