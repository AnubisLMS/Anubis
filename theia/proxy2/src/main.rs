mod proxy;
mod database;
mod token;
mod cli;
mod error;

use async_trait::async_trait;
use http::{Request, Response};
use hudsucker::{HttpHandler, HttpContext, RequestOrResponse};
use hyper::{Body, Method};

#[derive(Clone)]
pub struct MyHandler {
    db: database::AnubisDB,
    jwt: token::AnubisJWT,
}

#[async_trait]
impl HttpHandler for MyHandler {
    async fn handle_request(
        &mut self,
        _ctx: &HttpContext,
        req: Request<Body>,
    ) -> RequestOrResponse {
        println!("in {:?}", req);
        let (parts, body) = req.into_parts();

        println!("{:?}", parts.uri);

        RequestOrResponse::Request(
            Request::builder()
            .method(Method::GET)
            .uri("http://httpbin.org/ip")
            .body(Body::empty())
            .unwrap()
        )
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

    let args = cli::new();
    let db = database::AnubisDB::new(
        args.get_one::<String>("db_user").unwrap(),
        args.get_one::<String>("db_password").unwrap(),
        args.get_one::<String>("db_host").unwrap(),
        args.get_one::<String>("db_database").unwrap(),
        *args.get_one::<u16>("db_port").unwrap(),
        *args.get_one::<u32>("max_connections").unwrap(),
    );
    let jwt = token::AnubisJWT::new(args.get_one::<String>("secret_key").unwrap());

    let handler = MyHandler{
        db, jwt,
    };

    let proxy = proxy::Proxy::new(
        handler,
        args.get_one::<String>("host").unwrap(),
        *args.get_one::<u16>("port").unwrap(),
    );
    proxy.start()
}
