mod proxy;
mod database;
mod token;
mod cli;
mod error;

use clap::ArgMatches;
use std::collections::{HashMap, BTreeMap};
use async_trait::async_trait;
use http::{Request, Response, request, request::Parts};
use hudsucker::{HttpHandler, HttpContext, RequestOrResponse, tokio_tungstenite::tungstenite::handshake::headers};
use hyper::{Body, Method};
use tracing::{self, log::info, log::error};
use cookie::{Cookie, time::Duration};


#[derive(Clone)]
pub struct MyHandler {
    args: ArgMatches,
    db: database::AnubisDB,
    jwt: token::AnubisJWT,
}

fn parse_query(s: &str) -> HashMap<String, String> {
    let parsed_url: url::Url = match url::Url::parse(s) {
        Err(e) => {
            error!("Parsing url failed");
            url::Url::parse("http://localhost/").unwrap()
        },
        Ok(v) => v,
    };
    parsed_url.query_pairs().into_owned().collect()
}


#[test]
fn test_query_parse() {
    let query = "http://localhost/?abc=123&xyz=456";
    let parsed = parse_query(query);

    println!("{:?}", parsed);

    assert!(parsed.get("abc").is_some());
    assert!(parsed.get("xyz").is_some());
    assert!(parsed.get("notkey").is_none());

    assert_eq!(parsed.get("abc").expect("exp"), "123");
    assert_eq!(parsed.get("xyz").expect("exp"), "456");
}


fn pong_res() -> RequestOrResponse {
    RequestOrResponse::Response(
        Response::builder()
        .header("Content-Type", "text/plain")
        .body(Body::from("pong"))
        .unwrap()
    )
}


#[test]
fn test_pong_res() {
    pong_res();
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


#[test]
fn test_error_res() {
    error_res();
}


fn initialize(handler: &MyHandler, parts: request::Parts, _body: Body) -> RequestOrResponse {
    let uri = http::Uri::builder()
        .scheme("http") // tmp
        .authority("localhost") //  temp
        .path_and_query(parts.uri.path_and_query().unwrap().to_string())
        .build()
        .unwrap();

    // Get query from request
    let query = parse_query(&uri.to_string());
    if !query.contains_key("token") {
        error!("token key not found in query {:?}", query);
        return error_res()
    }

    // Verify token
    let query_token = query.get("token");
    if query_token.is_none() {
        error!("query token is None {:?}", query_token);
        return error_res()
    }
    let query_token = handler.jwt.verify(query_token.unwrap());
    if query_token.is_err() {
        error!("unable to verify key {:?}", query_token);
        return error_res()
    }
    let query_token = query_token.unwrap();

    // Figure out redirect domain
    let debug = handler.args.get_flag("debug");
    let domain = if debug { "localhost" } else { "anubis-lms.io" };

    // Create signed jwt
    let signed_token = match handler.jwt.sign(&query_token.netid, &query_token.session_id) {
        Ok(v) => v,
        Err(_) => return error_res(),
    };

    let cookie = Cookie::build("ide", signed_token)
        .domain(domain)
        .path("/")
        .max_age(Duration::new(6 * 3600, 0))
        .http_only(true)
        .finish();

    RequestOrResponse::Response(
        Response::builder()
        .status(302)
        .header("location", "/ide/")
        .header("Set-Cookie", cookie.to_string())
        .body(Body::from("redirecting..."))
        .unwrap()
    )
}


fn proxy(handler: &MyHandler, parts: request::Parts, body: Body) -> RequestOrResponse {
    if parts.headers.get("Cookies").is_some() {
        return error_res();
    }

    // parse cookies
    let cookie_header = parts.headers.get("Cookie");
    if cookie_header.is_none() {
        tracing::error!("no cookie");
        return error_res()
    }
    let cookie_header = cookie_header.unwrap().to_str().unwrap();
    let mut unverified_ide_token: Option<cookie::Cookie> = None;
    for cookie in Cookie::split_parse_encoded(cookie_header) {
        let cookie = cookie.unwrap();
        if cookie.name() == "ide" {
            unverified_ide_token = Some(cookie.clone())
        }
    }
    if unverified_ide_token.is_none() {
        error!("cookie does not contain token header {:?}", cookie_header);
        return error_res();
    }

    // verify token
    let unverified_ide_token = unverified_ide_token.unwrap().value().to_string();
    let ide_token = handler.jwt.verify(&unverified_ide_token);
    if ide_token.is_err() {
        error!("unauth token {:?}", ide_token);
        return error_res()
    }
    let ide_token = ide_token.unwrap();

    // get session from database
    let session = handler.db.get_session(&ide_token.session_id);
    if session.is_err() {
        error!("unable to get session from database {:?}", session);
        return error_res()
    }
    let session = session.unwrap();

    // FINALLY cluster address
    let cluster_address = session.cluster_address;

    // Construct new http parts
    let mut new_parts: http::request::Parts = parts;
    new_parts.uri = http::Uri::builder()
        .scheme("http")
        .authority(cluster_address) // cluster address for routing
        .path_and_query(new_parts.uri.path_and_query().unwrap().to_string())
        .build()
        .unwrap();

    let proxy_req = Request::from_parts(new_parts, body);
    info!("going for proxy {:?}", proxy_req);

    RequestOrResponse::Request(proxy_req)
}


#[test]
fn test_cookie() {
    let cookie_header = "token=123; bac=xzy";
    for cookie in Cookie::split_parse_encoded(cookie_header) {
        let cookie = cookie.unwrap();
        match cookie.name() {
            "token" => assert_eq!(cookie.value(), "123"),
            "bac" => assert_eq!(cookie.value(), "xzy"),
            _ => panic!("unknown cookie"),
        }
    }
}   


#[async_trait]
impl HttpHandler for MyHandler {
    async fn handle_request(
        &mut self,
        _ctx: &HttpContext,
        req: Request<Body>,
    ) -> RequestOrResponse {
        info!("in {:?}", req);
        let (parts, body) = req.into_parts();

        let path = parts.uri.path();
        let query = parts.uri.query();
        info!("{:?} {:?}", path, query);

        match path {
            "/ping" => return pong_res(),
            "/initialize" => return initialize(self, parts, body),
            _ => return proxy(self, parts, body),
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

    let host = args.get_one::<String>("host").unwrap().clone();
    let port = *args.get_one::<u16>("port").unwrap();

    let handler = MyHandler{
        args, db, jwt,
    };

    let proxy = proxy::Proxy::new(
        handler,
        &host,
        &port,
    );
    proxy.start()
}
