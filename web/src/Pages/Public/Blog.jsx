import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import {Switch, Route} from 'react-router-dom';

import AssignmentPost from '../../Components/Public/Blog/AssignmentPost';
import ElevatorPitchPost from '../../Components/Public/Blog/ElevatorPitchPost';
import AssignmentPackagingPost from '../../Components/Public/Blog/AssignmentPackagingPost';
import MidtermRetroPost from '../../Components/Public/Blog/MidtermRetroPost';
import TheiaIDEPost from '../../Components/Public/Blog/TheiaIDEPost';

const useStyles = makeStyles((theme) => ({
  card: {
    maxWidth: 1028,
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

const posts = [
  {
    Component: TheiaIDEPost,
    path: '/blog/anubis-cloud-ide',
  },
  {
    Component: MidtermRetroPost,
    path: '/blog/midterm-retro',
  },
  {
    Component: AssignmentPackagingPost,
    path: '/blog/assignment-packaging',
  },
  {
    Component: AssignmentPost,
    path: '/blog/packaging',
  },
  {
    Component: ElevatorPitchPost,
    path: '/blog/elevator-pitch',
  },
];


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
      <Switch>
        <Route exact path="/blog">
          {posts.map(({Component, path}, index) => (
            <Grid item xs={12} key={`post-preview-${index}`}>
              <Component classes={classes} preview={path}/>
            </Grid>
          ))}
        </Route>
        {posts.map(({Component, path}, index) => (
          <Route exact path={path} key={`post-${index}`}>
            <Component classes={classes} preview={false}/>
          </Route>
        ))}
      </Switch>

    </Grid>
  );
}
