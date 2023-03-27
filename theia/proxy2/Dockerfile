FROM rust:1.68 as builder
RUN set -eux; \
    rustup target add x86_64-unknown-linux-musl; \
    apt update; \
    apt install -y musl-tools musl-dev libssl-dev pkg-config; \
    update-ca-certificates

WORKDIR /opt/app
COPY . .
RUN cargo build --target x86_64-unknown-linux-musl --release

FROM scratch
COPY --from=builder /opt/app/target/x86_64-unknown-linux-musl/release/anubis-ide-proxy /anubis-ide-proxy
CMD ["/anubis-ide-proxy"]
