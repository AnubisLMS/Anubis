use crate::error::JWTError;

use std::{collections::BTreeMap, usize};
use serde::{Serialize, Deserialize};
use jsonwebtoken::{encode, decode, Header, Algorithm, Validation, EncodingKey, DecodingKey};
use std::time::{SystemTime, UNIX_EPOCH};


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

    pub fn sign(&self, netid: &str, session_id: &str) -> Result<String, JWTError> {
        let exp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        let exp = exp + std::time::Duration::from_secs(6 * 3600).as_secs();
        
        let claims = Claims{
            netid: netid.to_string(),
            session_id: session_id.to_string(),
            exp: exp.try_into().unwrap(),
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
fn test_sign_verify() {
    let _jwt = AnubisJWT::new("DEBUG");
    let signed = match _jwt.sign("abc123", "session_id_123") {
        Ok(v) => v,
        Err(e) => panic!("{:?}", e),
    };
    println!("signed = {:?}", signed);
    let claims = _jwt.verify(&signed);
    assert!(claims.is_ok())
}

#[test]
fn test_verify() {
    // jwt.encode({"netid":"123", "session_id": "123", "exp": datetime.now(tz=timezone.utc) + timedelta(days=365*10)}, "DEBUG")
    let signed = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuZXRpZCI6IjEyMyIsInNlc3Npb25faWQiOiIxMjMiLCJleHAiOjE5OTU5NDA4ODJ9.qqDju2U7nt0XNwa3khgzOcd2BmqKl7zr4A8QXpiNj8w";
    let _jwt = AnubisJWT::new("DEBUG");
    let claims = _jwt.verify(signed);
    match claims {
        Ok(_) => (),
        Err(e) => {
            panic!("{:?}", e);
        }
    }
    println!("signed = {:?}", signed);
}




// #[test]
// fn test_verify() {
//     let _jwt = AnubisJWT::new("abc");
//     let claims = _jwt.verify(TEST_ABC_123_SIGNED).expect("Could not verify token");
//     assert_eq!(claims.len(), 1);
//     assert!(claims.get("abc").is_some());
//     assert_eq!(claims.get("abc").expect("Could not get abc from claims"), "123");
// }
