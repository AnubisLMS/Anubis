import React, {useState} from 'react';

import Grid from '@material-ui/core/Grid';

import ReposTable from '../../Components/Public/Repos/ReposTable';
import StandardLayout from '../../Components/Layouts/StandardLayout';
import AuthContext from '../../Contexts/AuthContext';
import axios from 'axios';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import {useSnackbar} from 'notistack';
import standardErrorHandler from '../../Utils/standardErrorHandler';


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
          <Grid container spacing={1} justify={'center'}>
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

