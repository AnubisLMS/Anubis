import {useSnackbar} from 'notistack';
import axios from 'axios';

import standardStatusHandler from '../utils/standardStatusHandler';
import standardErrorHandler from '../utils/standardErrorHandler';

import {useEffect, useState} from 'react';

export default function useAdmin(base) {
  const {enqueueSnackbar} = useSnackbar();
  const [admins, setAdmins] = useState([]);
  useEffect(() => {
    axios.get(`/api/admin/courses/list/${base}s`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.users) {
        setAdmins(data.users);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);
  return admins;
}
