use http::uri::Authority;
use http::{Request};
use hudsucker::{
    HttpHandler,
    HttpContext,
    NoopHandler,
    Proxy as _Proxy,
    async_trait::async_trait,
    certificate_authority::CertificateAuthority,
    hyper::{Body, Client},
    rustls::ServerConfig,
};
use std::{net::SocketAddr, sync::Arc};
use futures::executor::block_on;
use std::net::{Ipv4Addr};

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
    port: u16,
    host: Ipv4Addr,
}

impl<T> Proxy<T> where T: HttpHandler {
    pub fn new(handler: T, host: &str, port: u16) -> Proxy<T> {
        
        // Construct address for server to listen on
        let host_ip: Ipv4Addr = host.parse().expect("msg");
        let address = SocketAddr::from((host_ip, port));
        
        Proxy {
            proxy: _Proxy::builder()
                .with_addr(address)
                .with_client(Client::new())
                .with_ca(NoCa)
                .with_http_handler(MyHandler)
                .with_http_handler(handler)
                .build(),
            port,
            host: host_ip,
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


#[test]
fn test_proxy_create() {
    // Just make sure we can create a proxy server
    let proxy = Proxy::new(NoopHandler::default(), "0.0.0.0", 3000);
    assert_eq!(proxy.host, Ipv4Addr::new(0, 0, 0, 0));
    assert_eq!(proxy.port, 3000);
}
