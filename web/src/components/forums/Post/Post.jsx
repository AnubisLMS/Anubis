import React from 'react';

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import VisibilityIcon from '@mui/icons-material/Visibility';
import CommentIcon from '@mui/icons-material/Comment';
import Button from '@mui/material/Button';

import Divider from '../../shared/Divider/Divider';
import CommentsList from '../CommentsList/CommentsList';
import {toRelativeDate} from '../../../utils/datetime';
import RichTextEditor from '../Editor/RichTextEditor';
import {useStyles} from './Post.styles';
import Publisher from '../Publisher/Publisher';
import AuthContext from '../../../context/AuthContext';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';


export default function Post({
  id,
  title,
  content,
  user,
  ownedByMe,
  seenCount,
  createdDate,
  updatedDate,
  comments,
  handleCreateComment,
}) {
  const classes = useStyles();
  const [commentPressed, setCommentPressed] = React.useState(false);

  console.log({user});

  const closePublisher = () => {
    setCommentPressed(false);
  };

  return (
    <Box className={classes.root} key={id}>
      <AuthContext.Consumer>
        {(currentUser) => (
          <React.Fragment>
            <Box className={classes.postInfoContainer}>
              <Box className={classes.profilePic}>
                <Typography>
                  {user[0]}
                </Typography>
              </Box>
              <Typography className={classes.User}>
                {user}
              </Typography>
              <Typography className={classes.whenPosted}>
                posted {toRelativeDate(new Date(createdDate))} (updated {toRelativeDate(new Date(updatedDate))})
              </Typography>
            </Box>
            <Typography className={classes.Title}>
              {title}
            </Typography>
            <Box className={classes.content}>
              <RichTextEditor content={content} readOnly={true} enableToolbar={false}/>
            </Box>
            <Box className={classes.extraInfo}>
              <Box className={classes.infoToolbar}>
                <Box className={classes.infoContainer}>
                  <VisibilityIcon className={classes.icon}/>
                  <Typography>
                    {seenCount}
                  </Typography>
                </Box>
                <Box className={classes.infoContainer}>
                  <CommentIcon className={classes.icon}/>
                  <Typography>
                    {comments.length}
                  </Typography>
                </Box>
              </Box>
              <Box>
                {ownedByMe &&
                  <Button
                    variant={'contained'}
                    color={'primary'}
                    sx={{mr: 1}}
                    startIcon={<EditIcon/>}
                    // onClick={() => setCommentPressed(true)}
                  >
                    Edit
                  </Button>
                }
                {commentPressed ||
                  <Button
                    variant={'contained'}
                    color={'primary'}
                    startIcon={<AddIcon/>}
                    onClick={() => setCommentPressed(true)}
                  >
                    Add Comment
                  </Button>
                }
              </Box>
            </Box>
            <Divider/>
            {commentPressed && (
              <Publisher
                mode='comment'
                handlePublish={handleCreateComment}
                setOpen={closePublisher}
                onClose={() => setCommentPressed(false)}
              />
            )}
            <Box className={classes.commentListContainer}>
              <CommentsList comments={comments} handleCreateComment={handleCreateComment}/>
            </Box>
          </React.Fragment>
        )}
      </AuthContext.Consumer>
    </Box>
  );
};

