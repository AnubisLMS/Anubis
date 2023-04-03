FROM rust:1.68 as builder
RUN set -eux; \
    rustup target add x86_64-unknown-linux-musl; \
    apt update; \
    apt install -y musl-tools musl-dev libssl-dev pkg-config; \
    update-ca-certificates

WORKDIR /opt/app
COPY Cargo.toml Cargo.lock /opt/app/
RUN set -eux; \
    mkdir -p src; \
    echo 'fn main() {}' >> src/main.rs; \
    cargo build --target x86_64-unknown-linux-musl --release; \
    rm -rf src target

COPY . .
RUN set -eux; cargo build --target x86_64-unknown-linux-musl --release

FROM alpine
ENV RUST_BACKTRACE=1
COPY --from=builder /opt/app/target/x86_64-unknown-linux-musl/release/anubis-ide-proxy /anubis-ide-proxy
ENTRYPOINT ["/anubis-ide-proxy"]
