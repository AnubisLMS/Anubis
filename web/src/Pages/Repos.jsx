import React from 'react';
import {Redirect} from 'react-router-dom';

import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import ReposTable from '../Components/Repos/ReposTable';
import useGet from '../hooks/useGet';


export default function Repos() {
  const {loading, error, data} = useGet('/api/public/repos');

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  return (
    <Grid
      container
      direction="column"
      justify="center"
      alignItems="center"
    >
      <Grid item xs={12}>
        <ReposTable rows={data.repos}/>
      </Grid>
    </Grid>
  );
}
