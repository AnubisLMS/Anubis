# https://github.com/theia-ide/theia-apps/tree/master/theia-cpp-docker

FROM registry.digitalocean.com/anubis/theia-base:python-3.10.0 as theia

ENV GO_VERSION=1.17 \
  GOOS=linux \
  GOARCH=amd64 \
  GOROOT=/opt/go \
  GOPATH=/opt/go-tools
ENV PATH=$GOROOT/bin:$GOPATH/bin:$PATH

USER root
RUN set -ex; \
  cd /home/anubis; \
  mkdir -p $GOROOT; \
  mkdir -p $GOPATH; \
  chown -R anubis:anubis $GOROOT; \
  curl -fsSL https://storage.googleapis.com/golang/go$GO_VERSION.$GOOS-$GOARCH.tar.gz | tar -C $(dirname $GOROOT) -xzv; \
  cd /home/anubis; \
  GOPROXY=direct go get -u -v github.com/uudashr/gopkgs/cmd/gopkgs; \
  go get -u -v github.com/mdempsky/gocode; \
  go get -u -v github.com/ramya-rao-a/go-outline; \
  go get -u -v github.com/acroca/go-symbols; \
  go get -u -v golang.org/x/tools/cmd/guru; \
  go get -u -v golang.org/x/tools/cmd/gorename; \
  go get -u -v github.com/fatih/gomodifytags; \
  go get -u -v github.com/haya14busa/goplay/cmd/goplay; \
  go get -u -v github.com/josharian/impl; \
  go get -u -v github.com/tylerb/gotype-live; \
  go get -u -v github.com/rogpeppe/godef; \
  go get -u -v github.com/zmb3/gogetdoc; \
  go get -u -v golang.org/x/tools/cmd/goimports; \
  go get -u -v github.com/sqs/goreturns; \
  go get -u -v winterdrache.de/goformat/goformat; \
  go get -u -v golang.org/x/lint/golint; \
  go get -u -v github.com/cweill/gotests/...; \
  go get -u -v honnef.co/go/tools/...; \
  GO111MODULE=on go get github.com/golangci/golangci-lint/cmd/golangci-lint; \
  GO111MODULE=on go get golang.org/x/tools/gopls@latest; \
  go get -u -v github.com/mgechev/revive; \
  go get -u -v github.com/sourcegraph/go-langserver; \
  go get -u -v github.com/go-delve/delve/cmd/dlv; \
  go get -u -v github.com/davidrjenni/reftools/cmd/fillstruct; \
  go get -u -v github.com/go-delve/delve/cmd/dlv; \
  go get -u -v github.com/stamblerre/gocode; \
  cp /opt/go-tools/bin/gocode /opt/go-tools/bin/gocode-gomod; \
  cp /opt/go-tools/bin/godef /opt/go-tools/bin/godef-gomod; \
  echo 'export GO111MODULE=on' >> .bashrc; \
  sed -i 's/"default": "goreturns"/"default": "goformat"/' \
    /opt/theia/plugins/vscode-go/extension/package.json

COPY supervisord.conf /supervisord.conf
USER anubis
