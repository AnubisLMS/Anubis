const axios = require('axios');

const devmode = process.env.REACT_APP_DEV;

const api = axios.create({
  baseURL: devmode ? 'https://api.localhost/public/' : 'https://api.nyu.cool/public/',
  timeout: 1000,
});

module.exports = {
  api,
};
