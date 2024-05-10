use anyhow::Result;
use serde::{Deserialize, Serialize};
use sqlx::{prelude::FromRow, MySqlPool};

#[derive(Deserialize, Serialize, FromRow)]
struct TheiaSession {
    cluster_address: Option<String>,
}

pub async fn get_cluster_address(pool: &MySqlPool, session_id: &str) -> Result<String> {
    let row: Option<TheiaSession> = sqlx::query_as(
        r#"
        SELECT cluster_address
        FROM theia_session
        WHERE id = ? AND active = 1
        "#,
    )
    .bind(session_id)
    .fetch_optional(pool)
    .await?;

    match row {
        Some(session) => {
            if let Some(cluster_address) = session.cluster_address {
                Ok(cluster_address)
            } else {
                Err(anyhow::anyhow!("cluster address not found"))
            }
        }
        None => Err(anyhow::anyhow!("session not found")),
    }
}

pub async fn update_last_proxy_time(session_id: &str, pool: &MySqlPool) -> Result<()> {
    sqlx::query(
        r#"
        UPDATE theia_session
        SET last_proxy = NOW()
        WHERE id = ?
        "#,
    )
    .bind(session_id)
    .execute(pool)
    .await?;

    Ok(())
}
