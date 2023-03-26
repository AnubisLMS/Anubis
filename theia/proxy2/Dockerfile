FROM rust:1.68 as builder
WORKDIR /opt/app
COPY . .
RUN cargo build --release

FROM debian:bullseye-slim
WORKDIR /opt/app
COPY --from=builder /opt/app/target/release/anubis-ide-proxy /opt/app/anubis-ide-proxy
CMD ["./anubis-ide-proxy"]
