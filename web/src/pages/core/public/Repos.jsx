import React, {useState} from 'react';

import Grid from '@mui/material/Grid';

import ReposTable from '../../../components/core/Repos/ReposTable';
import StandardLayout from '../../../components/shared/Layouts/StandardLayout';
import AuthContext from '../../../context/AuthContext';
import axios from 'axios';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import {useSnackbar} from 'notistack';
import standardErrorHandler from '../../../utils/standardErrorHandler';


const Repos = () => {
  const [rows, setRows] = useState([]);
  const [reset, setReset] = useState(0);
  const {enqueueSnackbar} = useSnackbar();

  React.useEffect(() => {
    axios.get('/api/public/repos').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.repos) {
        setRows(data.repos);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  return (
    <AuthContext.Consumer>
      {(user) => (
        <StandardLayout description={`${user?.name}'s Repos`}>
          <Grid container spacing={1} justifyContent={'center'}>
            <Grid item xs={12}>
              <ReposTable rows={rows} setReset={setReset}/>
            </Grid>
          </Grid>
        </StandardLayout>
      )}
    </AuthContext.Consumer>
  );
};

export default Repos;

