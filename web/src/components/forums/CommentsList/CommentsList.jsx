import React, {useState} from 'react';

import Box from '@mui/material/Box';
import Comment from '../Comment/Comment';
import Publisher from '../Publisher/Publisher';
import {useStyles} from './CommentsList.styles';

export default function CommentsList({comments, handleCreateComment}) {
  const classes = useStyles();

  const [isReplying, setIsReplying] = useState(false);

  const Thread = ({hasChildren, comment}) => {
    const [collapsed, setCollapsed] = useState(false);

    return (
      <Box className={classes.thread}>
        <Comment
          threadStart
          user={comment.display_name}
          id={comment.id}
          content={comment.content}
          createdDate={comment.created}
          hasReplies={comment.children.length > 0}
          replyCount={comment.children.length}
          handleCollapse={() => setCollapsed(!collapsed)}
          isCollapsed={collapsed}
          handleReply={() => setIsReplying(!isReplying)}
        />
        {(hasChildren && !collapsed) &&
          <Box className={classes.replies}>
            {comment.children.length > 0 && comment.children.map((childComment, index) => (
              <Comment
                key={`child-${childComment.display_name}-${index}`}
                user={childComment.display_name}
                content={childComment.content}
                id={childComment.display_name}
                createdDate={childComment.created}
              />
            ))}
            {isReplying &&
              <Publisher mode="comment" setOpen={setIsReplying}
                handlePublish={(comment) => handleCreateComment({...comment, comment_id: comment.id})}/>
            }
          </Box>
        }
      </Box>
    );
  };

  return (
    <Box className={classes.root}>
      {comments && comments.map((comment, index) => (
        <Thread
          key={`${comment.display_name}-${index}`}
          hasChildren={comment.children.length > 0}
          comment={comment}
        />
      ))}
    </Box>
  );
}
