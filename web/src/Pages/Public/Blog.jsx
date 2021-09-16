import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import {Route, Switch} from 'react-router-dom';

import Divider from '@material-ui/core/Divider';

import BlogPost from '../../Components/Public/Blog/BlogPost';

import posts from '../../Content';

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
    color: theme.palette.colors.orange,
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
  divider: {
    height: 3,
    marginTop: theme.spacing(3),
  },
  root: {
    margin: theme.spacing(5, 0),
  },
}));

export default function Blog() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Grid
        container
        direction="column"
        justify="center"
        alignItems="center"
        spacing={4}
      >
        <Switch>
          <Route exact path="/blog">
            {posts.map((post, index) => (
              <Grid item xs = {12} key = {`post-${index}-${post.title}`}>
                <BlogPost
                  isHighlight = {post.isHighlight}
                  get = {post.get}
                  slug = {post.slug}
                  title = {post.title}
                  author = {post.author}
                  authorImage = {post.authorImage}
                  date = {post.date}
                  preview = {true}
                />
                {post.isHighlight && <Divider className={classes.divider} variant={'middle'}/>}
              </Grid>
            ))}
          </Route>
          {posts.map((post, index) => (
            <Route exact path={`/blog/${post.slug}`} key={`post-${index}`}>
              <BlogPost
                get = {post.get}
                slug = {post.slug}
                title = {post.title}
                author = {post.author}
                authorImage = {post.authorImage}
                date = {post.date}
                preview = {false}
              />
            </Route>
          ))}
        </Switch>
      </Grid>
    </div>
  );
}
