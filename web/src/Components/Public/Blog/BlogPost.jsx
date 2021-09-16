import React, {useEffect, useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';

import CardActionArea from '@material-ui/core/CardActionArea';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import CardContent from '@material-ui/core/CardContent';
import Tooltip from '@material-ui/core/Tooltip';
import Card from '@material-ui/core/Card';
import ArrowBackIcon from '@material-ui/icons/ArrowBack';
import {useHistory} from 'react-router-dom';
import BlogContent from './BlogContent';

import axios from 'axios';

const useStyles = makeStyles((theme) => ({
  card: {
    maxWidth: 1024,
    position: 'relative',
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
  backButton: {
    position: 'absolute',
    top: theme.spacing(4),
    right: theme.spacing(4),
  },
  indentText: {
    marginLeft: theme.spacing(4),
    opacity: .6,
    marginTop: theme.spacing(4),
    fontSize: '1.2rem',
  },
}));


const parseContentForPreview = (content) => {
  return content.substring(content.lastIndexOf('<preview>') + '<preview>'.length, content.lastIndexOf('</preview>'));
};

const parseContentForFullView = (content) => {
  return content.replace('<preview>', '').replace('</preview>', ' ');
};

export default function BlogPost({get, slug, authorImage, isHighlight, title='', date='', author='', preview = false}) {
  const classes = useStyles();
  const history = useHistory();
  const [postContent, setPostContent] = useState(undefined);

  useEffect(() => {
    get()
      .then((file) => {
        axios.get(file.default)
          .then((file) => {
            setPostContent(preview ? parseContentForPreview(file.data) : parseContentForFullView(file.data));
          })
          .catch(((error) => console.log('FETCH/ERROR', error)));
      })
      .catch((error) => console.log('IMPORT/ERROR', error));
  }, []);

  return (
    <Card className={classes.card}>
      {preview &&
        <CardActionArea
          onClick = {() => history.push(`/blog/${slug}`)}
          style = {{focusHighlight: 'background-color: none'}}
        >
          <CardHeader
            avatar={<Avatar src={authorImage}/>}
            title={title}
            titleTypographyProps={{variant: 'h6'}}
            subheader={date}
          />
          <CardContent>
            {postContent &&
              <BlogContent content = {postContent} />
            }
          </CardContent>
        </CardActionArea>
      }
      {!preview &&
        <>
          <CardHeader
            avatar={<Avatar src={authorImage}/>}
            title={title}
            titleTypographyProps={{variant: 'h6'}}
            subheader={date}
          />
          <Tooltip
            className = {classes.backButton}
            disableFocusListener
            onClick = {() => history.push('/blog')}
            title='Back to /Blog'
          >
            <Button>
              <ArrowBackIcon/>
            </Button>
          </Tooltip>
          <CardContent>
            {postContent &&
              <BlogContent content = {postContent} />
            }
            <p className = {classes.indentText}> -  {author}</p>
          </CardContent>
        </>
      }
    </Card>
  );
}

