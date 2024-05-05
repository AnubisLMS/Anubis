FROM rust:latest as builder

WORKDIR /usr/src/app

COPY . .

RUN cargo build --release

FROM debian:bookworm

RUN apt-get update && apt-get install -y openssl libssl-dev ca-certificates

RUN useradd -ms /bin/bash app

WORKDIR /app

COPY --from=builder /usr/src/app/target/release/proxy-rs /app/proxy-rs

EXPOSE 5000

USER app

CMD ["./proxy-rs"]
