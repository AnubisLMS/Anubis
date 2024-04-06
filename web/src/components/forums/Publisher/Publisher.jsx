import React, {useState} from 'react';
import {Box, Button, DialogContent, DialogTitle, IconButton, InputBase, Switch, Typography} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import {useStyles} from './Publisher.styles';
import {useSnackbar} from 'notistack';
import MDEditor from '@uiw/react-md-editor';
import rehypeSanitize from 'rehype-sanitize';
import Divider from '@mui/material/Divider';

const modes = {
  'post': {
    title: 'Create Post',
    title_placeholder: 'Title',
    submit: 'Post',
  },
  'edit_post': {
    title: 'Edit Post',
    title_placeholder: 'Title',
    submit: 'Update',
  },
  'comment': {
    title: 'Create Comment',
    title_placeholder: '',
    submit: 'Comment',
  },
  'edit_comment': {
    title: 'Edit Comment',
    title_placeholder: '',
    submit: 'Update',
  },
};

export default function Publisher({
  mode = 'post',
  setOpen,
  onClose,
  handlePublish,
  initalTitle = '',
  initialContent = null,
  visibleToStudents = true,
  anonymous = false,
}) {
  // MUI theme-based css styles
  const classes = useStyles();
  // Form Data
  const [title, setTitle] = useState(initalTitle);
  const [content, setContent] = useState(initialContent);
  const [isVisibleToStudents, setIsVisisbleToStudents] = useState(visibleToStudents);
  const [isAnonymous, setIsAnonymous] = useState(anonymous);
  const {enqueueSnackbar} = useSnackbar();

  const isPost = mode === 'post' || mode === 'edit_post';

  const validatePost = () => {
    if (title && content) {
      handlePublish({
        title: title,
        content: content,
        visible_to_students: isVisibleToStudents,
        anonymous: isAnonymous,
      });
      if (onClose) onClose();
    } else if (content && !isPost) {
      handlePublish({
        content: content,
        anonymous: isAnonymous,
        visible_to_students: isVisibleToStudents,
      });
      if (onClose) onClose();
    } else {
      enqueueSnackbar('Post title and body cannot be empty', {variant: 'warning'});
    }
  };

  return (
    <Box className={classes.publisherContainer}>
      {isPost &&
        <diV>
          <DialogTitle className={classes.titleContainer}>
            <Box display="flex" alignItems="center">
              <Box flexGrow={1}> {modes[mode].title} </Box>
              <IconButton onClick={() => setOpen(false)}>
                <CloseIcon/>
              </IconButton>
            </Box>
          </DialogTitle>
          <Divider sx={{height: 1, backgroundColor: '#638efa'}} orientation="horizontal"/>
        </diV>
      }
      <DialogContent sx={{padding: 0}}>
        {isPost &&
          <InputBase
            sx={{pl: 1, paddingTop: 2, paddingBottom: 2, background: '#0d1117'}}
            placeholder={modes[mode].title_placeholder}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            fullWidth
          />
        }
        <div data-color-mode="dark">
          <MDEditor value={content} onChange={setContent} minHeight={200}
            previewOptions={{
              rehypePlugins: [[rehypeSanitize]],
            }}
            textareaProps={{
              placeholder: isPost ? 'Be specific and imagine you’re asking a question to another person. ' +
                        'Describe what you tried and what you expected to happen.' : '',
            }}
          />
        </div>
        <Box display="flex" alignItems="center" justifyContent="flex-start" gap="20px" padding="0px 10px"
          sx={{background: '#0d1117'}}
        >
          <div className={classes.switchContainer}>
            <Typography variant={'caption'}>TA&apos;s and Instructors only</Typography>
            <Switch checked={!isVisibleToStudents} onChange={() => setIsVisisbleToStudents(!isVisibleToStudents)}/>
          </div>
          <div className={classes.switchContainer}>
            <Typography variant={'caption'}>Anonymous</Typography>
            <Switch checked={isAnonymous} onChange={() => setIsAnonymous(!isAnonymous)}/>
          </div>
        </Box>
      </DialogContent>
      <Divider sx={{height: 1, backgroundColor: '#638efa'}} orientation="horizontal"/>
      <Button
        variant={'contained'}
        className={classes.submit}
        onClick={validatePost}
      >
        {modes[mode].submit}
      </Button>
    </Box>
  );
}
