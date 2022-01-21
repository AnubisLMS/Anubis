import React, {useState} from 'react';

import Dialog from '@material-ui/core/Dialog';
import Box from '@material-ui/core/Box';
import Input from '@material-ui/core/Input';
import Typography from '@material-ui/core/Typography';

import {useStyles} from './CreateDialog.styles';

export default function CreateDialog({
  mode = 'post',
  isOpen = false,
  onSubmit,
}) {
  const classes = useStyles();

  return (
    <Dialog
      isFullScreen
      open={isOpen}
      classes={{paper: classes.root}}
    >
      <Typography>
        {mode === 'post' ? 'Create a new post' : 'Create a new comment'}
      </Typography>
      <Input placeholder={'Post Title'} />
    </Dialog>
  );
}

