import React, {useState} from 'react';
import {Box, Button, DialogContent, DialogTitle, IconButton, Input, Switch, Typography} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import {useStyles} from './Publisher.styles';
import RichTextEditor from '../Editor/RichTextEditor';
import {useSnackbar} from 'notistack';

export default function Publisher({
  mode = 'post',
  setOpen,
  handlePublish,
}) {
  // MUI theme-based css styles
  const classes = useStyles();
  // Form Data
  const [title, setTitle] = useState('');
  const [content, setContent] = useState({});
  const [isVisibleToStudents, setIsVisisbleToStudents] = useState(true);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const {enqueueSnackbar} = useSnackbar();

  const isPost = mode === 'post';

  const validatePost = () => {
    if (title && content) {
      handlePublish({
        title: title,
        content: content,
        visible_to_students: isVisibleToStudents,
        anonymous: isAnonymous,
      });
    } else if (content && !isPost) {
      handlePublish({
        content: content,
        anonymous: isAnonymous,
        visible_to_students: isVisibleToStudents,
      });
    } else {
      enqueueSnackbar('Add content!', {variant: 'warning'});
    }
  };

  return (
    <Box className={classes.publisherContainer}>
      {isPost &&
        <DialogTitle className={classes.titleContainer}>
          <Box display="flex" alignItems="center">
            <Box flexGrow={1}>{isPost ? 'Create A New Post' : 'Create A New Comment'}</Box>
            <IconButton onClick={() => setOpen(false)}>
              <CloseIcon/>
            </IconButton>
          </Box>
        </DialogTitle>
      }
      <DialogContent sx={{padding: 0}}>
        {isPost &&
          <Input inputProps={{className: classes.inputTitle}} disableUnderline={true} fullWidth
            value={title} onChange={(e) => setTitle(e.target.value)} placeholder={'Put Title Here'}/>
        }
        {isPost ?
          <RichTextEditor setContent={setContent}/> :
          <RichTextEditor setContent={setContent} setOpen={setOpen}/>
        }
        <Box display="flex" alignItems="center" justifyContent="flex-start" gap="20px" padding="0px 10px">
          <div className={classes.switchContainer}>
            <Typography> Visibile to Students?</Typography>
            <Switch checked={isVisibleToStudents} onChange={() => setIsVisisbleToStudents(!isVisibleToStudents)}/>
          </div>
          <div className={classes.switchContainer}>
            <Typography>Anonymous?</Typography>
            <Switch checked={isAnonymous} onChange={() => setIsAnonymous(!isAnonymous)}/>
          </div>
        </Box>
      </DialogContent>
      <Button
        variant={'contained'}
        className={classes.submit}
        onClick={validatePost}
      >
        {isPost ? 'Post' : 'Comment'}
      </Button>
    </Box>
  );
}
