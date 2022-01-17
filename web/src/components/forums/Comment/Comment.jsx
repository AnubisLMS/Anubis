import React from 'react';

import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';

import {useStyles} from './Comment.styles';

export default function Comment({
  user,
  content,
  hasChildren,
  depth,
  createdDate,
}) {
  const classes = useStyles();
  return (
    <Box className={classes.root}>
      <Box className={classes.header}>
        <Box className={classes.profilePic}>
          <Typography className={classes.profilePicText}> {user[0]} </Typography>
        </Box>
        <Typography>{user}</Typography>
        <Typography className={classes.commentedWhen}>
          commented on {createdDate}
        </Typography>
      </Box>
      <Typography className={classes.content}>
        {content}
      </Typography>
    </Box>
  );
};

