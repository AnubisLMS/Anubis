import React, {useState, useRef, useEffect} from 'react';
import {EditorState, RichUtils, convertFromRaw, convertToRaw} from 'draft-js';
import Editor, {composeDecorators} from '@draft-js-plugins/editor';
import createResizablePlugin from '@draft-js-plugins/resizeable';
import EditorToolbar from './Toolbar/EditorToolbar';
import createImagePlugin from '@draft-js-plugins/image';
import {makeStyles} from '@mui/styles';
import {Box, IconButton} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

import 'draft-js/dist/Draft.css';
import './TextEditor.css';

const resizeablePlugin = createResizablePlugin();
const decorator = composeDecorators(
  resizeablePlugin.decorator,
);
const imagePlugin = createImagePlugin({decorator});

const useStyles = makeStyles((theme) => ({
  toolbarContainer: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderColor: theme.palette.white,
    borderTop: theme.spacing(0.1) + ' solid',
    borderBottom: theme.spacing(0.1) + ' solid',
  },
  editorContainer: {
    width: '100%',
  },
}));

export default function RichTextEditor({content = null, setContent = null, setOpen = null, readOnly = false,
  enableToolbar = true}) {
  const [editorState, setEditorState] = useState(EditorState.createEmpty());
  const editor = useRef(null);
  const classes = useStyles();

  if (!readOnly && setContent) {
    useEffect(() => {
      setContent(JSON.stringify(convertToRaw(editorState.getCurrentContent())));
    }, [editorState]);
  } else if (content) {
    useEffect(() => {
      setEditorState(EditorState.createWithContent(convertFromRaw(content)));
    }, []);
  }

  const handleKeyCommand = (command) => {
    const newState = RichUtils.handleKeyCommand(editorState, command);
    if (newState) {
      setEditorState(newState);
      return true;
    }
    return false;
  };
  return (
    <>
      {enableToolbar &&
      <Box className={classes.toolbarContainer}>
        <EditorToolbar editorState={editorState} setEditorState={setEditorState} imagePlugin={imagePlugin} />
        {
          setOpen &&
          <IconButton onClick={() => setOpen(false)}>
            <CloseIcon />
          </IconButton>
        }
      </Box>
      }
      <Editor
        ref={editor}
        className={classes.editorContainer}
        handleKeyCommand={handleKeyCommand}
        editorState={editorState}
        onChange={(editorState) => {
          setEditorState(editorState);
        }}
        readOnly={readOnly}
        plugins={[imagePlugin, resizeablePlugin]}
      />
    </>
  );
};
