const http = require("http")
const httpProxy = require("http-proxy");
const Knex = require("knex");
const jwt = require("jsonwebtoken");
const Cookie = require("universal-cookie");
const urlparse = require("url-parse");
const LRU = require("lru-cache");

const SECRET_KEY = process.env.SECRET_KEY ?? 'DEBUG';

const cache = new LRU(100);

const knex = Knex({
  client: "mysql",
  connection: {
    database: "anubis",
    user: "anubis",
    password: process.env.DB_PASSWORD || "anubis",
    host: process.env.DB_HOST || "127.0.0.1",
  }
});

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
  console.log(req.method, (new Date()).toISOString(), url.pathname, url.query);
};


const parse_req = req => {
  const url = urlparse(req.url);
  const {cookies} = new Cookie(req.headers.cookie);
  const query = new URLSearchParams(url.query);
  let {token} = cookies;
  token = authenticate(token);
  return {url, token, query, cookies};
};

const initialize = (req, res, url, query) => {
  // Authenticate the token in the http query
  console.log(`token: ${query.get('token')}`)
  const query_token = authenticate(query.get('token'));
  if (query_token === null) {
    res.writeHead(302, {location: 'https://anubis.osiris.services/error'});
    res.end('redirecting...');
    return;
  }

  // Set cookie for ide session & redirect
  const signed_token = jwt.sign({
    session_id: query_token.session_id,
  }, SECRET_KEY, {expiresIn: '6h'});
  res.writeHead(302, {
    location: '/', "Set-Cookie": `token=${signed_token}; Max-Age=${6 * 3600}; HttpOnly`
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
  const {url, token, query} = parse_req(req);
  log_req(req, url);

  switch (url.pathname) {
    case '/initialize':
      initialize(req, res, url, query)
      return;

    case '/ping':
      res.writeHead(200);
      res.end('pong');
      return;

    default:
      if (token === null) {
        res.writeHead(401)
        res.end('nah')
        return;
      }

      // updateProxyTime(token.session_id);
      get_session_ip(token.session_id).then((session_ip) => {
        proxy.web(req, res, {
          target: {
            host: session_ip,
            port: 5000
          }
        });
      })
  }
});

proxyServer.on("upgrade", function (req, socket) {
  const {token, url} = parse_req(req);
  log_req(req, url);

  if (token === null) {
    return
  }

  // updateProxyTime(token.session_id);
  get_session_ip(token.session_id).then((session_ip) => {
    proxy.ws(req, socket, {
      target: {
        host: session_ip,
        port: 5000
      }
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
