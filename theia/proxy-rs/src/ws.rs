use axum::extract::ws::{CloseFrame, Message as AxumMessage, WebSocket};
use futures_util::{SinkExt, StreamExt};
use tokio_tungstenite::tungstenite;
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message as TsMessage};

enum WebSocketMessageType {
    Axum(AxumMessage),
    Tungstenite(TsMessage),
}

struct WebSocketMessage {
    message: WebSocketMessageType,
}

impl WebSocketMessage {
    fn tungstenite(message: TsMessage) -> Self {
        Self {
            message: WebSocketMessageType::Tungstenite(message),
        }
    }

    fn axum(message: AxumMessage) -> Self {
        Self {
            message: WebSocketMessageType::Axum(message),
        }
    }

    fn into_tungstenite(self) -> TsMessage {
        match self.message {
            WebSocketMessageType::Axum(message) => match message {
                AxumMessage::Text(text) => TsMessage::Text(text),
                AxumMessage::Binary(binary) => TsMessage::Binary(binary),
                AxumMessage::Ping(ping) => TsMessage::Ping(ping),
                AxumMessage::Pong(pong) => TsMessage::Pong(pong),
                AxumMessage::Close(Some(close)) => {
                    TsMessage::Close(Some(tungstenite::protocol::frame::CloseFrame {
                        code: tungstenite::protocol::frame::coding::CloseCode::from(close.code),
                        reason: close.reason,
                    }))
                }
                AxumMessage::Close(None) => TsMessage::Close(None),
            },
            WebSocketMessageType::Tungstenite(message) => message,
        }
    }

    fn into_axum(self) -> AxumMessage {
        match self.message {
            WebSocketMessageType::Axum(message) => message,
            WebSocketMessageType::Tungstenite(message) => match message {
                TsMessage::Text(text) => AxumMessage::Text(text),
                TsMessage::Binary(binary) => AxumMessage::Binary(binary),
                TsMessage::Ping(ping) => AxumMessage::Ping(ping),
                TsMessage::Pong(pong) => AxumMessage::Pong(pong),
                TsMessage::Close(Some(close)) => AxumMessage::Close(Some(CloseFrame {
                    code: close.code.into(),
                    reason: close.reason,
                })),
                TsMessage::Close(None) => AxumMessage::Close(None),
                TsMessage::Frame(frame) => {
                    tracing::warn!("unexpected frame: {:?}", frame);
                    AxumMessage::Close(None)
                }
            },
        }
    }
}

pub async fn forward(url: String, client_ws: WebSocket) {
    let server_ws = match connect_async(url).await {
        Ok((ws, _)) => ws,
        Err(e) => {
            tracing::warn!("connect error: {}", e);
            return;
        }
    };

    tokio::spawn(async move {
        let (mut client_write, mut client_read) = client_ws.split();
        let (mut server_write, mut server_read) = server_ws.split();

        tokio::spawn(async move {
            while let Some(message) = client_read.next().await {
                match message {
                    Ok(message) => {
                        let message = WebSocketMessage::axum(message);
                        let res = server_write.send(message.into_tungstenite()).await;
                        if let Err(e) = res {
                            tracing::warn!("client write error: {}", e);
                            continue;
                        }
                    }
                    Err(e) => {
                        tracing::warn!("client read error: {}", e);
                        continue;
                    }
                }
            }
        });

        while let Some(message) = server_read.next().await {
            match message {
                Ok(message) => {
                    let message = WebSocketMessage::tungstenite(message);
                    let res = client_write.send(message.into_axum()).await;
                    if let Err(e) = res {
                        tracing::warn!("client write error: {}", e);
                        continue;
                    }
                }
                Err(e) => {
                    tracing::warn!("client read error: {}", e);
                    continue;
                }
            }
        }
    });
}
