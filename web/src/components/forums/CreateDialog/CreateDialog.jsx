import React, {useState, useRef} from 'react';
import {Dialog, DialogTitle, DialogContent, Box, Input, Typography, Button, Switch, IconButton} from '@mui/material';
import EditorToolbar from './Toolbar/EditorToolbar';
import {EditorState, RichUtils, convertToRaw} from 'draft-js';
import Editor, {composeDecorators} from '@draft-js-plugins/editor';
import createResizablePlugin from '@draft-js-plugins/resizeable';
import createImagePlugin from '@draft-js-plugins/image';
import CloseIcon from '@mui/icons-material/Close';
import {useStyles} from './CreateDialog.styles';

import 'draft-js/dist/Draft.css';
import './TextEditor.css';

const resizeablePlugin = createResizablePlugin();
const decorator = composeDecorators(
  resizeablePlugin.decorator,
);
const imagePlugin = createImagePlugin({decorator});

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
    const content = JSON.stringify(convertToRaw(editorState.getCurrentContent()));
    if (title && content) {
      handleCreatePost({
        title: title,
        content: content,
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
        <div className={classes.toolbarContainer}>
          <EditorToolbar editorState={editorState} setEditorState={setEditorState} imagePlugin={imagePlugin} />
        </div>
        <Editor
          ref={editor}
          handleKeyCommand={handleKeyCommand}
          editorState={editorState}
          onChange={(editorState) => {
            setEditorState(editorState);
          }}
          plugins={[imagePlugin, resizeablePlugin]}
        />
        <Box display="flex" alignItems="center" justifyContent="flex-start" gap="20px" padding="0px 10px">
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

