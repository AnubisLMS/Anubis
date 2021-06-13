import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';

import CardActionArea from '@material-ui/core/CardActionArea';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import {Link as RouterLink} from 'react-router-dom';

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
    color: theme.palette.text.secondary,
  },
  typography: {
    fontSize: 16,
    margin: theme.spacing(2),
  },
  sidebar: {
    fontSize: 14,
    fontStyle: 'italic',
    color: 'textSecondary',
    marginTop: theme.spacing(1),
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
    // width: '100%',
    height: 3,
    marginTop: theme.spacing(3),
  },
}));

export default function BlogPost({Preview, Post, title='', date='', author='', preview = false}) {
  const classes = useStyles();

  return (
    <Card className={classes.card}>
      <CardActionArea {...(!!preview ? {component: RouterLink, to: preview} : {})}>
        <CardHeader
          avatar={<Avatar src={'https://avatars.githubusercontent.com/u/36013983'}/>}
          title={title}
          titleTypographyProps={{variant: 'h6'}}
          subheader={date}
        />
        <CardContent>

          {/* Post Preview */}
          <Preview classes={classes} />

          {!preview ? (
            <React.Fragment>

              {/* Main Post Content */}
              <Post classes={classes}/>

              {/* Author */}
              <Typography variant={'body2'} className={classes.author}>
                - {author}
              </Typography>
            </React.Fragment>
          ) : null}
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
