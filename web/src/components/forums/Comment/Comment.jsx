import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';

import {useStyles} from './Comment.styles';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import {toRelativeDate} from '../../../utils/datetime';

export default function Comment({
  id,
  user,
  content,
  hasChildren,
  depth,
  createdDate,
}) {
  const classes = useStyles();
  const enqueueSnackbar = useSnackbar();

  const [children, setChildren] = useState(undefined);

  useEffect(() => {
    if (!hasChildren) {
      return null;
    }

    axios.get(`/api/public/forums/post/comment/${id}`)
      .then((response) => {
        const data = standardStatusHandler(response, enqueueSnackbar);
        console.log(data);
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  return (
    <Box className={classes.root}>
      <Box className={classes.header}>
        <Box className={classes.profilePic}>
          <Typography className={classes.profilePicText}> {user[0]} </Typography>
        </Box>
        <Typography>{user}</Typography>
        <Typography className={classes.commentedWhen}>
          commented {toRelativeDate(new Date(createdDate))}
        </Typography>
      </Box>
      <Typography className={classes.content}>
        {content}
      </Typography>
    </Box>
  );
};

