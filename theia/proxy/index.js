const http = require("http")
const httpProxy = require("http-proxy");
const streamify = require("stream-array");
const Knex = require("knex");
const jwt = require("jsonwebtoken");
const Cookie = require("universal-cookie");

const SECRET_KEY = process.env.SECRET_KEY || 'DEBUG';

const knex = Knex({
  client: "mysql",
  connection: {
    database : "anubis",
    user : "anubis",
    password : process.env.DB_PASSWORD || "anubis",
    host : process.env.DB_HOST || "127.0.0.1",
  }
});

const proxy = httpProxy.createProxyServer({
  target: {
    host: "theia",
    port: 5000
  },
  ws: true,
})

const authenticate = req => {
  const cookie = new Cookie(req.headers.cookie).cookies;
  if (cookie.token) {
    try {
      const decoded = jwt.verify(cookie.token, SECRET_KEY);
      
    } catch (e) {
      console.error('Caught auth error', e);
    }
  }

  return null;
};


var proxyServer = http.createServer(function (req, res) {
  console.log(req.method, (new Date()).toISOString(),  req.url);
  proxy.web(req, res);
});

proxyServer.on("upgrade", function (req, socket, head) {
  console.log(req.method, (new Date()).toISOString(), req.url);
  proxy.ws(req, socket, head);
});

console.log("starting http://localhost:5000/");
proxyServer.listen(5000);
