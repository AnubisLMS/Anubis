import React, {useState, useRef} from 'react';
import {Dialog, DialogTitle, DialogContent, Box, Input, Typography, Button, Switch, IconButton} from '@mui/material';
import makeStyles from '@mui/styles/makeStyles';
import Publisher from '../Publisher/Publisher';
export const useStyles = makeStyles((theme) => ({
  root: {
    width: '800px',
  },
}));

export default function CreateDialog({
  mode = 'post',
  open = false,
  setOpen,
  handleCreatePost,
}) {
  // MUI theme-based css styles
  const classes = useStyles();
  const [error, setError] = useState('');

  return (
    <Dialog
      open={open}
      classes={{paper: classes.root}}
      onClose={() => setOpen(false)}
    >
      {error}
      <Publisher mode={mode} setOpen={setOpen} handlePublish={handleCreatePost}/>
    </Dialog>
  );
}

