import React from 'react';
import {Redirect} from 'react-router-dom';

import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import ReposTable from '../../Components/Public/Repos/ReposTable';
import useGet from '../../hooks/useGet';
import Typography from '@material-ui/core/Typography';
import AuthContext from '../../Contexts/AuthContext';


export default function Repos() {
  const [{loading, error, data}] = useGet('/api/public/repos/');

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  return (
    <Grid
      container
      justify="center"
      alignItems="center"
      spacing={4}
    >
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <AuthContext.Consumer>
          {(user) => (
            <Typography variant={'subtitle1'} color={'textSecondary'}>
              {user.name}&apos;s Repos
            </Typography>
          )}
        </AuthContext.Consumer>
      </Grid>
      <Grid item/>

      <Grid item xs={12} md={10} lg={8}>
        <ReposTable rows={data.repos}/>
      </Grid>
    </Grid>
  );
}
