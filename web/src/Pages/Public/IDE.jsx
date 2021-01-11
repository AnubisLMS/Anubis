import React from 'react';
import {Redirect} from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import useSubscribe from '../../hooks/useSubscribe';
import IDETable from '../../Components/Public/IDE/IDETable';
import IDEInstructions from '../../Components/Public/IDE/IDEInstructions';
import IDEHeader from '../../Components/Public/IDE/IDEHeader';


export default function IDE() {
  const [{loading, error, data}] = useSubscribe(
    '/api/public/ide/list',
    1000,
    (_data) => new Array(..._data.sessions).every((item) => (
      item.state !== 'Initializing' && item.state !== 'Ending'
    )),
  );

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  const {session_available} = data;

  return (
    <Grid
      container
      direction="row"
      justify="center"
      alignItems="center"
      spacing={6}
    >

      <Grid item xs={12}>
        <IDEHeader session_available={session_available}/>
      </Grid>

      <Grid item xs={12}>
        <IDEInstructions/>
      </Grid>

      <Grid item xs={12}>
        <IDETable rows={new Array(...data.sessions)}/>
      </Grid>
    </Grid>
  );
}
