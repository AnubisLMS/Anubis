FROM rust:1.68 as builder
WORKDIR /opt/app
COPY . .
RUN cargo build --release

FROM debian:bullseye-slim
COPY --from=builder /opt/app/target/anubis-ide-proxy /usr/local/bin/anubis-ide-proxy
CMD ["./anubis-ide-proxy"]
