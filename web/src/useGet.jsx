import React, {useState} from "react";
import axios from 'axios';

/**
 * loading, error, data
 * @param path
 * @param params
 */
export default function useGet(path, params) {
  const [state, setState] = useState({
    loading: true, error: null, data: null
  });

  if (!params) params = {};
  if (!state.loading) return state;

  const searchParams = new URLSearchParams();
  for (const key of Object.keys(params)) {
    searchParams.append(key, params[key]);
  }

  axios.get(path, searchParams)
    .then(function (data) {
      setState({
        loading: false,
        error: !data.data.success,
        data: data.data.data,
      });
    })
    .catch(function (error) {
      setState({
        loading: false,
        error,
        data: null
      });
    });

  return state;
}