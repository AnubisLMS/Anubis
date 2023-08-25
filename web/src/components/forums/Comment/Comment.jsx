import React, {useState} from 'react';
import {useSnackbar} from 'notistack';

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import ReplyIcon from '@mui/icons-material/Reply';
import EditIcon from '@mui/icons-material/Edit';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import {useStyles} from './Comment.styles';
import {toRelativeDate} from '../../../utils/datetime';
import Publisher from '../Publisher/Publisher';
import RichTextEditor from '../Editor/RichTextEditor';

export default function Comment({
  threadStart = false,
  id,
  user = 'Anonymous',
  content,
  createdDate,
  hasReplies,
  ownedByMe,
  handleCollapse,
  isCollapsed,
  replyCount,
  handleReply,
  handleEditComment,
}) {
  const classes = useStyles();
  const enqueueSnackbar = useSnackbar();
  const [children, setChildren] = useState(undefined);
  const [openEditor, setOpenEditor] = useState(false);

  return (
    <Box className={classes.root}>
      {!openEditor ? (
        <>
          <Box className={classes.header}>
            <Box className={classes.profilePic}>
              <Typography className={classes.profilePicText}> {user[0]} </Typography>
            </Box>
            <Typography>{user}</Typography>
            <Typography className={classes.commentedWhen}>
              {toRelativeDate(new Date(createdDate))}
            </Typography>
          </Box>
          <Box className={classes.content}>
            <RichTextEditor content={content} readOnly={true} enableToolbar={false} />
          </Box>
        </>
      ) :
        (
          <Publisher
            mode="edit_comment"
            initialContent={content}
            setOpen={setOpenEditor}
            onClose={() => {}}
            handlePublish={(content) => handleEditComment(id, content)}
          />
        )
      }
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
            <ReplyIcon className={classes.icon} />
            <Typography className={classes.actionItem}>Reply</Typography>
          </Box>
        }
        {ownedByMe &&
          <Box
            onClick={() => setOpenEditor(true)}
            className={classes.action}
          >
            <EditIcon className={classes.icon}/>
            <Typography className={classes.actionItem}>Edit</Typography>
          </Box>
        }
      </Box>
    </Box>
  );
};

