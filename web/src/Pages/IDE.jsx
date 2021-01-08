import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import {Redirect} from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import useSubscribe from '../hooks/useSubscribe';
import IDETable from '../Components/IDE/IDETable';
import IDEInstructions from '../Components/IDE/IDEInstructions';
import IDEHeader from '../Components/IDE/IDEHeader';


const useStyles = makeStyles((theme) => ({
  root: {
    flexShrink: 0,
    marginLeft: theme.spacing(2.5),
  },
  instructions: {
    paddingTop: theme.spacing(1),
    paddingLeft: theme.spacing(1),
  },
  available: {
    display: 'inline',
  },
}));


export default function IDE() {
  const classes = useStyles();
  const {loading, error, data} = useSubscribe(
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
    <div className={classes.root}>
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
    </div>
  );
}
