import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';

import AssignmentPost from '../../Components/Public/Blog/AssignmentPost';
import ElevatorPitchPost from '../../Components/Public/Blog/ElevatorPitchPost';
import AssignmentPackagingPost from '../../Components/Public/Blog/AssignmentPackagingPost';

const useStyles = makeStyles((theme) => ({
  card: {
    maxWidth: 1028,
  },
  imgbox: {
    width: '100%',
    marginTop: theme.spacing(2),
  },
  img: {
    width: '100%',
    height: '100%',
  },
  media: {
    height: 0,
  },
  media16x9: {
    height: 0,
    paddingTop: '56.25%', // 16:9
  },
  title: {
    fontSize: 20,
    color: 'textPrimary',
  },
  subtitle: {
    fontSize: 18,
    marginTop: theme.spacing(4),
    marginBottom: theme.spacing(1),
    marginLeft: theme.spacing(1),
    color: 'textSecondary',
  },
  typography: {
    fontSize: 16,
    margin: theme.spacing(2),
  },
  sidebar: {
    fontSize: 14,
    fontStyle: 'italic',
    color: 'textSecondary',
    marginLeft: theme.spacing(4),
  },
  author: {
    margin: theme.spacing(4),
    fontSize: 16,
  },
  markdown: {
    margin: theme.spacing(1),
  },
  bullet: {
    display: 'inline-block',
    margin: '0 2px',
    transform: 'scale(0.8)',
  },
}));


export default function Blog() {
  const classes = useStyles();

  return (
    <Grid
      container
      direction="column"
      justify="center"
      alignItems="center"
      spacing={4}
    >
      <Grid item xs={12}>
        <AssignmentPackagingPost classes={classes}/>
      </Grid>
      <Grid item xs={12}>
        <AssignmentPost classes={classes}/>
      </Grid>
      <Grid item xs={12}>
        <ElevatorPitchPost classes={classes}/>
      </Grid>
    </Grid>
  );
}
