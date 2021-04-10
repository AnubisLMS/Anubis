import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';

import John from '../../Components/Public/About/John';
import Somto from '../../Components/Public/About/Somto';
import Description from '../../Components/Public/About/Description';

const useStyles = makeStyles((theme) => ({
  root: {
    maxWidth: 512,
  },
  authors: {
    paddingTop: theme.spacing(5),
  },
}));


export default function About() {
  const classes = useStyles();

  return (
    <Grid
      container
      direction="column"
      justify="center"
      alignItems="center"
      spacing={4}
    >
      {/* description */}
      <Grid item xs={12}>
        <Description className={classes.root}/>
      </Grid>
      {/* END Jumbotron */}

      {/* Author description */}
      <Grid
        container
        direction={'row'}
        spacing={3}
        alignItems={'center'}
        justify={'center'}
        className={classes.authors}
      >
        <Grid item xs={12}>
          <Typography variant="h5" style={{textAlign: 'center'}}>
            About the Authors
          </Typography>
        </Grid>

        <Grid item xs={12} md={6}>
          <John/>
        </Grid>
        <Grid item xs={12} md={6}>
          <Somto/>
        </Grid>
      </Grid>
      {/* END Author section */}

    </Grid>
  );
}
