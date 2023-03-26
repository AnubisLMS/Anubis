use http::uri::Authority;
use hudsucker::{
    builder,
    HttpHandler,
    HttpContext,
    NoopHandler,
    Proxy as _Proxy,
    async_trait::async_trait,
    certificate_authority::CertificateAuthority,
    hyper::{Body, Client, Request, Response},
    rustls::ServerConfig,
    RequestOrResponse,
};
use std::{net::SocketAddr, sync::Arc};


pub struct NoCa;

#[async_trait]
impl CertificateAuthority for NoCa {
    async fn gen_server_config(&self, _: &Authority) -> Arc<ServerConfig> {
        unreachable!();
    }
}

#[derive(Clone)]
pub struct MyHandler;

#[async_trait]
impl HttpHandler for MyHandler {
    async fn should_intercept(&mut self, _: &HttpContext, _: &Request<Body>) -> bool {
        false
    }
}


pub fn new() -> builder::ProxyBuilder<builder::WantsHandlers<hyper::client::HttpConnector, NoCa, MyHandler, NoopHandler>> {
    return _Proxy::builder()
        .with_addr(SocketAddr::from(([127, 0, 0, 1], 3000)))
        .with_client(Client::new())
        .with_ca(NoCa)
        .with_http_handler(MyHandler);
}