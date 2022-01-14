import {useEffect, useState} from 'react';
import axios from 'axios';

/**
 * loading, error, data
 * @param path
 * @param interval
 * @param until
 * @param callback
 */
export default function useSubscribe(path, interval, until, callback) {
  const [state, setState] = useState({
    loading: true, error: null, data: {},
  });

  function reset() {
    setState({
      loading: true, error: null, data: null,
    });
  }


  useEffect(() => {
    if (state.error || (!state.loading && !!until(state.data))) {
      return;
    }
    const timer = setInterval(() => {
      if (state.error || (!state.loading && !!until(state.data))) {
        clearInterval(timer);
      }
      axios.get(path)
        .then(function(data) {
          const newState = {
            loading: false,
            error: !data.data.success,
            data: data.data.data,
          };
          setState(newState);
          if (callback) {
            callback(state, newState);
          }
        })
        .catch(function(error) {
          if (!error.response) {
            console.error(error);
            return;
          }
          if (error.response.status === 401) {
            window.location = '/api/public/auth/login';
          }
          setState({
            loading: false,
            error,
            data: null,
          });
          clearInterval(timer);
        });
    }, interval);

    return () => clearInterval(timer);
  });

  return [state, reset];
}
