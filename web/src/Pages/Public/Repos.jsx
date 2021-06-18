import React from 'react';
import {Redirect} from 'react-router-dom';

import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';


import ReposTable from '../../Components/Public/Repos/ReposTable';
import useGet from '../../hooks/useGet';
import StandardLayout from '../../Components/Layouts/StandardLayout';


export default function Repos() {
  const [{loading, error, data}] = useGet('/api/public/repos/');

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  return (
    <StandardLayout description={'Assignment Repos'}>
      <Grid container spacing={1} justify={'center'}>
        <Grid item xs={12}>
          <ReposTable rows={data.repos}/>
        </Grid>
      </Grid>
    </StandardLayout>
  );
}
