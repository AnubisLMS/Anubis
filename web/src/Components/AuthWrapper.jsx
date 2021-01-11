import React from 'react';
import CircularProgress from '@material-ui/core/CircularProgress';
import useGet from '../hooks/useGet';
import {Redirect} from 'react-router-dom';
import AuthContext from '../Contexts/AuthContext';

export default function AuthWrapper({children}) {
  const [{loading, error, data}, reset] = useGet('/api/public/auth/whoami');

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  let user;
  if (data) {
    user = data.user;
    user.reset = reset;
  } else {
    user = null;
  }

  return (
    <AuthContext.Provider value={user}>
      {children}
    </AuthContext.Provider>
  );
}
