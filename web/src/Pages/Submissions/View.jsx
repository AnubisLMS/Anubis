import SubmissionTable from "./SubmissionTable"
import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import { Typography } from "@material-ui/core";
import Grow from '@material-ui/core/Grow'
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
      fontWeight:300
  }
}));

export default function SubmissionsView() {
  const classes = useStyles();
  return (
    <div className={classes.root}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
            
            
              <Typography variant="h6"> 
                    Intro to Operating Systems 
              </Typography>
              <Typography variant="body1" className={classes.subtitle} >
                    CS-3224
              </Typography>
        </Grid>
        <Grid item xs={6}>
        <Grow
          in= "true"
          style={{ transformOrigin: '0 0 0' }}
          {...({ timeout: 300 } )}
        >          
            <SubmissionTable />   
        </Grow>     
        </Grid>
      </Grid>
    </div>
  );
}