import {useState} from 'react';
import axios from 'axios';

/**
 * loading, error, data
 * @param path
 * @param params
 */
export default function useGet(path, params) {
  const [state, setState] = useState({
    loading: true, error: null, data: null,
  });

  function reset() {
    setState({
      loading: true, error: null, data: null,
    });
  }

  if (!params) params = {};
  if (!state.loading) return [state, reset];

  if (state.loading) {
    axios.get(path, {params})
      .then(function(response) {
        setState({
          loading: false,
          error: !response.data.success,
          data: response.data.data,
        });
      })
      .catch(function(error) {
        if (!error.response) {
          setState({loading: false, error: error, data: null});
        } else if (error.response.status === 401) {
          window.location = '/error';
        } else {
          setState({
            loading: false,
            error,
            data: null,
          });
        }
      });
  }

  return [state, reset];
}
