import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import ReplyIcon from '@mui/icons-material/Reply';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import {useStyles} from './Comment.styles';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import {toRelativeDate} from '../../../utils/datetime';

export default function Comment({
  threadStart = false,
  id,
  user = 'Anonymous',
  content,
  createdDate,
  hasReplies,
  handleCollapse,
  isCollapsed,
  replyCount,
  handleReply,
}) {
  const classes = useStyles();
  const enqueueSnackbar = useSnackbar();

  const [children, setChildren] = useState(undefined);

  return (
    <Box className={classes.root}>
      <Box className={classes.header}>
        <Box className={classes.profilePic}>
          <Typography className={classes.profilePicText}> {user[0]} </Typography>
        </Box>
        <Typography>{user}</Typography>
        <Typography className={classes.commentedWhen}>
          {toRelativeDate(new Date(createdDate))}
        </Typography>
      </Box>
      <Typography className={classes.content}>
        {content}
      </Typography>
      <Box className={classes.replyActions}>
        {hasReplies &&
          <Box
            className={classes.action}
            onClick={handleCollapse}
          >
            {isCollapsed ? <ExpandLessIcon className={classes.icon} /> : <ExpandMoreIcon className={classes.icon} />}
            <Typography className={classes.actionItem}>View Replies </Typography>
          </Box>
        }
        {threadStart &&
          <Box
            onClick={handleReply}
            className={classes.action}
          >
            <ReplyIcon className={classes.icon}/>
            <Typography className={classes.actionItem}>Reply</Typography>
          </Box>
        }
      </Box>
    </Box>
  );
};

