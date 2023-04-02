mod proxy;
mod database;
mod token;
mod cli;
mod error;

use clap::ArgMatches;
use std::collections::{HashMap, BTreeMap};
use async_trait::async_trait;
use http::{Request, Response, request};
use hudsucker::{HttpHandler, HttpContext, RequestOrResponse};
use hyper::{Body, Method};
use tracing;

#[derive(Clone)]
pub struct MyHandler {
    args: ArgMatches,
    db: database::AnubisDB,
    jwt: token::AnubisJWT,
}

fn parse_query(s: &str) -> HashMap<String, String> {
    let parsed_url = url::Url::parse(s).unwrap();
    parsed_url.query_pairs().into_owned().collect()
}

fn pong_res() -> RequestOrResponse {
    RequestOrResponse::Response(
        Response::builder()
        .header("Content-Type", "text/plain")
        .body(Body::from("pong"))
        .unwrap()
    )
}

fn error_res() -> RequestOrResponse {
    RequestOrResponse::Response(
        Response::builder()
        .status(302)
        .header("location", "/error")
        .body(Body::from("redirtecting..."))
        .unwrap()
    )
}

fn initialize(handler: &MyHandler, _ctx: &HttpContext, parts: request::Parts, body: Body) -> RequestOrResponse {
    // Get query from request
    let query = parse_query(parts.uri.query().unwrap());
    if !query.contains_key("token") {
        return error_res()
    }

    // Verify token
    let query_token = match handler.jwt.verify(query.get("token").expect("No token")) {
        Ok(v) => v,
        Err(_) => return error_res(),
    };

    // Figure out redirect domain
    let debug = handler.args.get_flag("debug");
    let domain = if debug { "localhost" } else { "anubis-lms.io" };

    // Create signed jwt
    let jwt_content: BTreeMap<String, String> = BTreeMap::from([
        ("netid".to_owned(), query_token.get("netid").unwrap().to_owned()),
        ("session_id".to_owned(), query_token.get("session_id").unwrap().to_owned()),
    ]);
    let signed_token = match handler.jwt.sign(&jwt_content) {
        Ok(v) => v,
        Err(_) => return error_res(),
    };

    RequestOrResponse::Response(
        Response::builder()
        .status(302)
        .header("location", "/ide/")
        .header("Set-Cookie", format!("ide={}; Path=/; Domain={}; Max-Age={}; HttpOnly", signed_token, domain, 6 * 3600))
        .body(Body::from("redirecting..."))
        .unwrap()
    )
}

fn proxy(handler: &MyHandler, _ctx: &HttpContext, parts: request::Parts, body: Body) -> RequestOrResponse {
    if parts.headers.get("Cookies").is_some() {
        return error_res();
    }

    let cookies = parse_query(parts.headers.get("Cookies").unwrap().to_str().unwrap_or_default());
    tracing::info!("cookies = {:?}", cookies);


    pong_res()
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

        let path = parts.uri.path();
        let query = parts.uri.query();
        println!("{:?} {:?}", path, query);

        match path {
            "/ping" => return pong_res(),
            "/initialize" => return initialize(self, _ctx, parts, body),
            _ => return proxy(self, _ctx, parts, body),
        }
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
        args, db, jwt,
    };

    let proxy = proxy::Proxy::new(
        handler,
        args.get_one::<String>("host").unwrap(),
        args.get_one::<u16>("port").unwrap(),
    );
    proxy.start()
}
