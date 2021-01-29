import React, {useState} from 'react';
import AuthContext from '../Contexts/AuthContext';
import axios from 'axios';
import standardStatusHandler from '../Utils/standardStatusHandler';
import {useSnackbar} from 'notistack';

export default function AuthWrapper({children}) {
  const {enqueueSnackbar} = useSnackbar();
  const [user, setUser] = useState(null);
  const [reset, setReset] = useState(0);

  React.useEffect(() => {
    axios.get('/api/public/auth/whoami').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      setUser({
        setReset,
        ...(data?.user ?? {}),
      });
    });
  }, [reset]);

  return (
    <AuthContext.Provider value={user}>
      {children}
    </AuthContext.Provider>
  );
}
