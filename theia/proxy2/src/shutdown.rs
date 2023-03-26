use tokio;

pub async fn shutdown_sig() {
    tokio::signal::ctrl_c().await.expect("abc");
}