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
use std::{net::SocketAddr, sync::Arc, rc::Rc};
use futures::executor::block_on;

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

pub struct Proxy<T> where T: HttpHandler {
    proxy: _Proxy<hyper::client::HttpConnector, NoCa, T, NoopHandler>,
}

impl<T> Proxy<T> where T: HttpHandler {
    pub fn new(handler: T) -> Proxy<T> {
        Proxy {
            proxy: _Proxy::builder()
            .with_addr(SocketAddr::from(([127, 0, 0, 1], 3000)))
            .with_client(Client::new())
            .with_ca(NoCa)
            .with_http_handler(MyHandler)
            .with_http_handler(handler)
            .build()
        }
    }

    pub fn start(self) {
        if let Err(e) = block_on(self.proxy.start(Self::shutdown_sig())) {
            tracing::error!("error {}", e);
        }
    }

    async fn shutdown_sig() {
        tokio::signal::ctrl_c().await.expect("abc");
    }
}


