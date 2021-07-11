FROM golang:1.16

RUN mkdir -p /build/
COPY *.mod *.go *.sum /build/
WORKDIR /build
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags '-w -s' -installsuffix cgo -a -o out/puller


  # present the result within a slimmed image
FROM scratch

COPY --from=0 /build/out/puller /puller
ENTRYPOINT /puller
