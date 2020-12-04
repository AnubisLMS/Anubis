const http = require("http")
const httpProxy = require("http-proxy");
const Knex = require("knex");
const jwt = require("jsonwebtoken");
const Cookie = require("universal-cookie");
const k8s = require('@kubernetes/client-node');
const Redis = require("redis");
const urlparse = require("url-parse");
const crypto = require("crypto")

const SECRET_KEY = process.env.SECRET_KEY || 'DEBUG';
const k8s_client = new k8s.KubeConfig();
k8s_client.loadFromCluster();
const k8s_api = k8s_client.makeApiClient((k8s.CoreV1Api));

const redis = Redis.createClient({ host: "redis" });

redis.on("error", function(error) {
  console.error(error);
});

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
});



const authenticate = token => {
  if (token) {
    try {
      const decoded = jwt.verify(token, SECRET_KEY);
      return decoded.netid;
    } catch (e) {
      console.error('Caught auth error', e);
    }
  }

  return null;
};

const initialize_session = (req, res) => {
  redis.smembers("theia-sessions", data => {
    console.log(data)
  })
}


var proxyServer = http.createServer(function (req, res) {
  const url = urlparse(req.url);
  const cookie = new Cookie(req.headers.cookie).cookies;
  const {token, assignment} = cookie;
  console.log(req.method, (new Date()).toISOString(),  url.pathname, url.query);

  switch (url.pathname) {
    case '/initialize':
      if (!(token && assignment)) {
        res.writeHead(302, {location: ''});
        res.end('redirecting...');
        return;
      }
      // initialize new session
      break

    case '/ping':
      res.writeHead(200);
      res.end('pong');
      return;

    default:
      proxy.web(req, res);
  }
});

proxyServer.on("upgrade", function (req, socket, head) {
  console.log(req.method, (new Date()).toISOString(), req.url);
  proxy.ws(req, socket, head);
});

console.log("starting http://localhost:5000/");
proxyServer.listen(5000);
