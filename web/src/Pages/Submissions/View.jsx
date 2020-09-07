import SubmissionTable from "./SubmissionTable"
import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import {Typography} from "@material-ui/core";
import Zoom from '@material-ui/core/Zoom'

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
  subtitle:
    {
      fontWeight: 300
    }
}));

export default function SubmissionsView() {
  const classes = useStyles();
  return (
    <div className={classes.root}>
      <Grid container 
            direction="row" 
            justify="center" 
            alignItems="center"
            spacing={6}>
        <Grid item xs={12}>

          <Typography variant="h6">
            Intro to Operating Systems
          </Typography>
          <Typography variant="body1" className={classes.subtitle}>
            CS-3224
          </Typography>
        </Grid>
        <Zoom in={true} timeout={350}>
          <Grid item xs>
            <SubmissionTable/>
          </Grid>
        </Zoom>
      </Grid>
    </div>
  );
}