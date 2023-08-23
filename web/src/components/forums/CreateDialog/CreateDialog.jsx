import React, {useState} from 'react';
import {Dialog} from '@mui/material';
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
  ...rest
}) {
  // MUI theme-based css styles
  const classes = useStyles();
  return (
    <Dialog
      open={open}
      classes={{paper: classes.root}}
      onClose={() => setOpen(false)}
    >
      <Publisher
        mode={mode}
        setOpen={setOpen}
        handlePublish={handleCreatePost}
        {...rest}
      />
    </Dialog>
  );
}

