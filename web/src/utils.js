const axios = require('axios');

const devmode = process.env.REACT_APP_DEV;
const apiUrl = devmode ? 'http://localhost:5000/api' : 'https://anubis.osiris.services/api'

const api = axios.create({
  baseURL: apiUrl,
  timeout: 1000,
});

module.exports = {
  api,
};
