use std::fmt;
use std::error;

#[derive(Debug, Clone)]
pub struct JWTError {pub message: String}
impl fmt::Display for JWTError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {write!(f, "{}", self.message)}
}
impl error::Error for JWTError {}


#[derive(Debug, Clone)]
pub struct DBError {pub message: String}
impl fmt::Display for DBError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {write!(f, "{}", self.message)}
}
impl error::Error for DBError {}


#[derive(Debug, Clone)]
pub struct AuthError {pub message: String}
impl fmt::Display for AuthError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {write!(f, "{}", self.message)}
}
impl error::Error for AuthError {}


