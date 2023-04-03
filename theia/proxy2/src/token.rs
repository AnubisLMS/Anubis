use crate::error::JWTError;

use hmac::{Hmac, Mac};
use std::{collections::BTreeMap, usize};
use serde::{Serialize, Deserialize};
use jsonwebtoken::{encode, decode, Header, Algorithm, Validation, EncodingKey, DecodingKey};



type MapSxS = BTreeMap<String, String>;

#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    pub netid: String,
    pub session_id: String,
    pub exp: usize,
}

#[derive(Debug, Clone)]
pub struct AnubisJWT {
    key: String,
}


impl AnubisJWT {
    pub fn new(key: &str) -> AnubisJWT {
        tracing::info!("Init JWT keychain");
        tracing::info!("key = {:?}", key);

        AnubisJWT { 
            key: key.to_string(),
        }
    }

    pub fn sign(&self, netid: &str, session_id: &str, exp: &usize) -> Result<String, JWTError> {
        let claims = Claims{
            netid: netid.to_string(),
            session_id: session_id.to_string(),
            exp: *exp,
        };
        let token = encode(&Header::new(Algorithm::HS256), &claims, &EncodingKey::from_secret(self.key.as_ref()));

        if token.is_err() {
            tracing::error!("Unable to sign token {:?}", token.clone().err().unwrap());
            return Err(JWTError { message: token.err().unwrap().to_string() })
        }
        
        Ok(token.unwrap())
    }

    pub fn verify(&self, data: &str) -> Result<Claims, JWTError> {
        let token = decode::<Claims>(data, &DecodingKey::from_secret(self.key.as_ref()), &Validation::default());

        if token.is_err() {
            let e = token.err().unwrap();
            tracing::error!("Unable to decode token {:?} {:?}", data, e);
            return Err(JWTError{message: e.to_string()})
        }

        Ok(token.unwrap().claims)
    }
}


// // {"abc": "123"} 
// // signed with key "abc"
// // with sha384


#[test]
fn test_sign() {
    let signed = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuZXRpZCI6InN1cGVydXNlciIsImV4cCI6MTY4MDUwNTc0MSwic2Vzc2lvbl9pZCI6IjRjMTA3MTgzLWJlOTMtNGYxNS05MmI0LTc1YTZhNWYzNTVmOCJ9.7NIF0okZAPNstMGh6O-vrjsMk_83vtrY2tes81vY6e4";
    let _jwt = AnubisJWT::new("DEBUG");
    let claims = _jwt.verify(signed);
    assert!(claims.is_ok())
}


// #[test]
// fn test_verify() {
//     let _jwt = AnubisJWT::new("abc");
//     let claims = _jwt.verify(TEST_ABC_123_SIGNED).expect("Could not verify token");
//     assert_eq!(claims.len(), 1);
//     assert!(claims.get("abc").is_some());
//     assert_eq!(claims.get("abc").expect("Could not get abc from claims"), "123");
// }
