use hmac::{Hmac, Mac};
use jwt::{AlgorithmType, Header, Token, VerifyWithKey, Verified, SignWithKey, Store};
use sha2::Sha384;
use std::{collections::BTreeMap, error::Error};
use std::fmt;

type MapSxS = BTreeMap<String, String>;
type ShaT = Sha384;

#[derive(Debug, Clone)]
pub struct AnubisJWT {
    key: Hmac<ShaT>
}

#[derive(Debug, Clone)]
pub struct AnubisJWTError {message: String}
impl fmt::Display for AnubisJWTError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {write!(f, "{}", self.message)}
}
impl Error for AnubisJWTError {}


impl AnubisJWT {
    pub fn new(key: &str) -> AnubisJWT {
        AnubisJWT { 
            key: Hmac::<ShaT>::new_from_slice(key.as_bytes())
            .expect("Unable to initialize hmac for JWT")
        }
    }

    pub fn sign(self, data: &MapSxS) -> Result<String, AnubisJWTError> {
        let header = Header {
            algorithm: AlgorithmType::Hs384,
            ..Default::default()
        };

        let mut claims = BTreeMap::new();
        for (key, value) in data {
            claims.insert(key, value);
        }
        
        let token = Token::new(header, claims).sign_with_key(&self.key);
        let token = match token {
            Err(e) => return Err(AnubisJWTError{message: e.to_string()}),
            Ok(v) => v,
        };
        
        Ok(token.as_str().to_string())
    }

    pub fn verify(self, data: String) -> Result<MapSxS, AnubisJWTError> {
        let parsed: std::result::Result<_, jwt::Error> = data.verify_with_key(&self.key);

        let token: Token<Header, BTreeMap<String, String>, _> = match parsed {
            Err(e) => return Err(AnubisJWTError{message: e.to_string()}),
            Ok(v) => v
        };

        Ok(token.claims().clone())
    }
}


// {"abc": "123"} 
// signed with key "abc"
// with sha384
static TEST_ABC_123_SIGNED: &str = "eyJhbGciOiJIUzM4NCJ9.eyJhYmMiOiIxMjMifQ.7Z2-aBvv2PfR0dJ0LzRNI0XgWYkITV86ojAJ_gnFx2jNrpWKbny2kcHCKwwoK0Qi";

#[test]
fn test_sign() {
    let _jwt = AnubisJWT::new("abc");
    let claims = BTreeMap::from([("abc".to_owned(), "123".to_owned())]);
    let token = _jwt.sign(&claims).expect("ERR");
    assert_eq!(token, TEST_ABC_123_SIGNED);
}

#[test]
fn test_verify() {
    let _jwt = AnubisJWT::new("abc");
    let claims = _jwt.verify(TEST_ABC_123_SIGNED.to_string()).expect("Could not verify token");
    assert_eq!(claims.len(), 1);
    assert!(claims.get("abc").is_some());
    assert_eq!(claims.get("abc").expect("Could not get abc from claims"), "123");
}
