import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button'; 
import { Typography } from '@material-ui/core';
const useStyles = makeStyles((theme) => ({
  root: {
    '& > *': {
      margin: theme.spacing(1),
      width: '25ch',
    },
    flexGrow: 1,
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.secondary,
    width:200
  },
  margin: {
    margin: theme.spacing(1),
  },
  extendedIcon: {
    marginRight: theme.spacing(1),
  },
}));

export default function GetGithubUsername(data) {
  const classes = useStyles();

  return (
    <Grid container justify="left"  spacing={4}>
      
        <Grid item xs={12}>
          <Typography style={{fontWeight:14}}>
         Please enter your Github Username.
         </Typography>
        </Grid>
        

          <Paper>
          <Grid item>
            <form className={classes.root} noValidate autoComplete="off">
                <TextField id="outlined-basic" label="Username" variant="outlined" />
            </form>

            
            </Grid>
            
            <Grid item>
            <div>
            <Button variant="outlined" size="medium" color="primary" className={classes.margin}>
              Submit
            </Button>
            </div>
            </Grid>
            </Paper>


            </Grid>

       
        
  );
}