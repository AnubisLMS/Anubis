import React, {useState} from 'react';

import Dialog from '@material-ui/core/Dialog';
import Box from '@material-ui/core/Box';
import Input from '@material-ui/core/Input';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Switch from '@material-ui/core/Switch';

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

