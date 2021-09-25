const http = require("http")
const httpProxy = require("http-proxy");
const Knex = require("knex");
const jwt = require("jsonwebtoken");
const Cookie = require("universal-cookie");
const urlparse = require("url-parse");
const LRU = require("lru-cache");

const SECRET_KEY = process.env.SECRET_KEY ?? 'DEBUG';
const DEBUG = process.env.DEBUG === '1';

/**
 * Least Recently Used Cache for ip address lookups. Creating an
 * in-memory cache of session id -> session ip address cuts down
 * on latency and round trips to the database.
 */
const cache = new LRU(100);

/**
 * Knex connection to the database.
 */
const knex = Knex({
  client: "mysql2",
  connection: {
    database: "anubis",
    user: "anubis",
    password: process.env.DB_PASSWORD || "anubis",
    host: process.env.DB_HOST || "127.0.0.1",
    port: process.env.DB_PORT || "3306",
  }
});

/**
 * Proxy server with websocket forwarding enabled.
 */
const proxy = httpProxy.createProxyServer({
  ws: true,
});


const authenticate = token => {
  if (token) {
    try {
      const decoded = jwt.verify(token, SECRET_KEY);
      return decoded;
    } catch (e) {
      console.error('Caught auth error', e);
    }
  }

  return null;
};

const get_session_ip = session_id => {
  const cached_ip = cache.get(session_id);
  if (cached_ip) {
    return new Promise((resolve) => {
      resolve(cached_ip);
    })
  }
  return new Promise((resolve) => {
    knex
      .first('cluster_address')
      .from('theia_session')
      .where('id', session_id)
      .then((row) => {
        console.log(`cluster_ip ${row.cluster_address}`)
        if (row.cluster_address) {
          console.log(`caching cluster ip ${row.cluster_address}`)
          cache.set(session_id, row.cluster_address);
        }
        resolve(row.cluster_address);
      });
  })
}


const log_req = (req, url) => {
  if (url.pathname !== '/ping') {
    console.log(req.method, (new Date()).toISOString(), url.pathname, url.query);
  }
};

const parse_port = req => {
  const portr = /\/proxy:\d+|\/proxy%3A\d+|\/proxy%3a\d+/;
  const portm = req.url.match(portr) ?? [];
  let port = 5000;
  if (portm.length === 1) {
    [, port] = portm[0].split(':');
    req.url = req.url.replaceAll(portm[0], '');
  }
  return port ?? 5000;
}

const parse_req = req => {
  const port = parse_port(req);
  const url = urlparse(req.url);
  const {cookies} = new Cookie(req.headers.cookie);
  const query = new URLSearchParams(url.query);
  let {ide} = cookies;
  token = authenticate(ide);
  return {url, token, query, cookies, port};
};

const initialize = (req, res, url, query) => {
  // Authenticate the token in the http query
  const query_token = authenticate(query.get('token'));
  if (query_token === null) {
    res.writeHead(302, {location: 'https://anubis.osiris.services/error'});
    res.end('redirecting...');
    return;
  }

  let domain = DEBUG ? 'localhost' : 'anubis.osiris.services';

  // Set cookie for ide session & redirect
  const signed_token = jwt.sign({
    session_id: query_token.session_id,
  }, SECRET_KEY, {expiresIn: '6h'});
  res.writeHead(302, {
    location: '/ide/', "Set-Cookie": `ide=${signed_token}; Path=/; Domain=${domain}; Max-Age=${6 * 3600}; HttpOnly`
  })
  res.end('redirecting...')
};

function changeTimezone(date, ianatz) {
  // suppose the date is 12:00 UTC
  var invdate = new Date(date.toLocaleString('en-US', {
    timeZone: ianatz
  }));

  // then invdate will be 07:00 in Toronto
  // and the diff is 5 hours
  var diff = date.getTime() - invdate.getTime();

  // so 12:00 in Toronto is 17:00 UTC
  return new Date(date.getTime() - diff); // needs to substract

}

const updateProxyTime = session_id => {
  const now = changeTimezone(new Date(), 'America/New_York');
  knex('theia_session')
    .where({id: session_id})
    .update({last_proxy: now})
    .then(() => null);
};


var proxyServer = http.createServer(function (req, res) {
  let {url, token, query, port} = parse_req(req);
  log_req(req, url);
  
  if ((req.headers?.host ?? '').startsWith('ide8000.'))
    port = 8000;

  switch (url.pathname) {
    case '/initialize':
      initialize(req, res, url, query);
      return;

    case '/ping':
      if (token !== null) updateProxyTime(token.session_id);
      res.writeHead(200);
      res.end('pong');
      return;

    default:
      if (token === null) {
        res.writeHead(401);
        res.end('Please start an ide at https://anubis.osiris.services and click go to ide.');
        return;
      }

      if (port !== 5000 && (port < 8000 || port > 8010)) {
        res.writeHead(400)
        res.end('Only valid proxy ports are 8000-8010');
        return;
      }

      get_session_ip(token.session_id).then((host) => {
        proxy.web(req, res, {
          target: {host, port}
        });
      })
  }
});

proxyServer.on("upgrade", function (req, socket) {
  const {token, url, port} = parse_req(req);
  log_req(req, url);

  if (token === null) {
    return
  }

  // updateProxyTime(token.session_id);
  get_session_ip(token.session_id).then((host) => {
    proxy.ws(req, socket, {
      target: {host, port}
    });
  });
});

proxyServer.on("error", function (error) {
  console.error(error);
})

proxy.on('error', function (error) {
  console.error(error);
})

process.on('uncaughtException', function (error) {
  console.error(error);
})

console.log("starting at 0.0.0.0:5000");
console.log(`SECRET_KEY = ${SECRET_KEY}`);
proxyServer.listen(5000);
