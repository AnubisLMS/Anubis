import React, {useState, useRef} from 'react';
import {Dialog, DialogTitle, DialogContent, Box, Input, Typography, Button, Switch, IconButton} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import {useStyles} from './CreateDialog.styles';
import RichTextEditor from '../RichTextEditor/RichTextEditor';

export default function CreateDialog({
  mode = 'post',
  open = false,
  setOpen,
  handleCreatePost,
}) {
  // MUI theme-based css styles
  const classes = useStyles();
  let getContent;
  // Form Data
  const [title, setTitle] = useState('');
  const [isVisibleToStudents, setIsVisisbleToStudents] = useState(true);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [error, setError] = useState('');
  const validatePost = () => {
    const content = getContent();
    if (title && content) {
      handleCreatePost({
        title: title,
        content: content,
        visible_to_students: isVisibleToStudents,
        anonymous: isAnonymous,
      });
    };
  };

  return (
    <Dialog
      isFullScreen
      open={open}
      classes={{paper: classes.root}}
      onClose={() => setOpen(false)}
    >
      {error}
      <DialogTitle className={classes.titleContainer}>
        <Box display="flex" alignItems="center">
          <Box flexGrow={1} >{mode === 'post' ? 'Create A New Post' : 'Create A New Comment'}</Box>
          <Box>
            <IconButton onClick={(e) => setOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>
      </DialogTitle>
      <DialogContent sx={{padding: 0}}>
        <Input inputProps={{className: classes.inputTitle}} disableUnderline={true} fullWidth
          value={title} onChange={(e) => setTitle(e.target.value)} placeholder={'Put Title Here'} />
        <RichTextEditor getContent={getContent}/>
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
      <Button className={classes.submit} onClick={validatePost}> Post </Button>
    </Dialog>
  );
}

