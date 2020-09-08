import React, {useState, useEffect} from "react";
import axios from 'axios';

/**
 * loading, error, data
 * @param path
 * @param interval
 * @param until
 */
export default function useSubscribe(path, interval, until, callback) {
  const [state, setState] = useState({
    loading: true, error: null, data: {}
  });

  useEffect(() => {
    if (state.error || (!state.loading && !!until(state.data)))
      return ;
    const timer = setInterval(() => {
      if (state.error || (!state.loading && !!until(state.data)))
        clearInterval(timer);
      axios.get(path)
        .then(function (data) {
          const newState = {
            loading: false,
            error: !data.data.success,
            data: data.data.data,
          }
          setState(newState);
          callback(state, newState);
        })
        .catch(function (error) {
          setState({
            loading: false,
            error,
            data: null
          });
          clearInterval(timer);
        });
    }, interval)

    return () => clearInterval(timer);
  })

  return state;
}