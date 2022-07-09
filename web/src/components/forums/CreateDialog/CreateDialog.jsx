import React, {useState} from 'react';

import Dialog from '@mui/material/Dialog';
import Box from '@mui/material/Box';
import Input from '@mui/material/Input';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Switch from '@mui/material/Switch';

import {Editor, EditorState} from 'draft-js';

import {useStyles} from './CreateDialog.styles';

export default function CreateDialog({
  mode = 'post',
  isOpen = false,
  handleCreatePost,
}) {
  const classes = useStyles();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isVisibleToStudents, setIsVisisbleToStudents] = useState(true);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [error, setError] = useState('');

  const validatePost = () => {
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
      open={isOpen}
      classes={{paper: classes.root}}
    >
      {error}
      <Typography>
        {mode === 'post' ? 'Create a new post' : 'Create a new comment'}
      </Typography>
      <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder={'Post Title'} />
      <TextField value={content} onChange={(e) => setContent(e.target.value)}/>
      <div className={classes.switchContainer}>
        <p> Visibile to Students ? </p>
        <Switch checked={isVisibleToStudents} onChange={() => setIsVisisbleToStudents(!isVisibleToStudents)}/>
      </div>
      <div className={classes.switchContainer}>
        <p>Anonymous ? </p>
        <Switch checked={isAnonymous} onChange={() => setIsAnonymous(!isAnonymous)}/>
      </div>
      <Button onClick={validatePost}> Post </Button>
    </Dialog>
  );
}

