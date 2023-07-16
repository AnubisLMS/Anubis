import React, {useState, useRef} from 'react';

import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import Box from '@mui/material/Box';
import Input from '@mui/material/Input';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Switch from '@mui/material/Switch';
import EditorToolbar from './Toolbar/EditorToolbar';
import {Editor, EditorState, RichUtils, convertToRaw} from 'draft-js';
import CloseIcon from '@mui/icons-material/Close';
import IconButton from '@mui/material/IconButton';

import 'draft-js/dist/Draft.css';
import './TextEditor.css';
import {useStyles} from './CreateDialog.styles';

export default function CreateDialog({
  mode = 'post',
  open = false,
  setOpen,
  handleCreatePost,
}) {
  // MUI theme-based css styles
  const classes = useStyles();

  // Form Data
  const [title, setTitle] = useState('');
  const [isVisibleToStudents, setIsVisisbleToStudents] = useState(true);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [editorState, setEditorState] = useState(EditorState.createEmpty());
  const editor = useRef(null);

  const [error, setError] = useState('');
  const validatePost = () => {
    if (title && content) {
      handleCreatePost({
        title: title,
        content: JSON.stringify(convertToRaw(editorState.getCurrentContent())),
        visible_to_students: isVisibleToStudents,
        anonymous: isAnonymous,
      });
    };
  };

  const handleKeyCommand = (command) => {
    const newState = RichUtils.handleKeyCommand(editorState, command);
    if (newState) {
      setEditorState(newState);
      return true;
    }
    return false;
  };

  return (
    <Dialog
      isFullScreen
      open={open}
      classes={{paper: classes.root}}
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
        <Input inputProps={{className: classes.inputTitle}} fullWidth
          value={title} onChange={(e) => setTitle(e.target.value)} placeholder={'Put Title Here'} />
        <div className={classes.toolbarContainer}>
          <EditorToolbar editorState={editorState} setEditorState={setEditorState}/>
        </div>
        <Editor
          ref={editor}
          handleKeyCommand={handleKeyCommand}
          editorState={editorState}
          onChange={(editorState) => {
            setEditorState(editorState);
          }}
        />
        <Box display="flex" alignItems="center" justifyContent="flex-start" gap="20px" padding="10px">
          <div className={classes.switchContainer}>
            <p> Visibile to Students?</p>
            <Switch checked={isVisibleToStudents} onChange={() => setIsVisisbleToStudents(!isVisibleToStudents)}/>
          </div>
          <div className={classes.switchContainer}>
            <p>Anonymous?</p>
            <Switch checked={isAnonymous} onChange={() => setIsAnonymous(!isAnonymous)}/>
          </div>
        </Box>
      </DialogContent>
      <Button className={classes.submit} onClick={validatePost}> Post </Button>
    </Dialog>
  );
}

