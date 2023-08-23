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

/**
 * Rich text editor used to display and publish data
 * @param {Object} content - the content of the editor, use this when we need to display data or set data prior to edit
 * @param {Function} setContent - the function to set the content of the editor, use this when we need to publish data
 * @param {Function} setOpen - the function to set the open state of the editor, called when close button clicked
 * @param {Boolean} readOnly - whether or not the editor is read only
 * @param {Boolean} enableToolbar - whether or not to show the toolbar
 * @returns {JSX.Element} - the rich text editor
 */
export default function RichTextEditor({content = null, setContent = null, setOpen = null, readOnly = false,
  enableToolbar = true}) {
  const [editorState, setEditorState] = useState(EditorState.createEmpty());
  const editor = useRef(null);
  const classes = useStyles();

  if (setContent && !readOnly) {
    useEffect(() => {
      // If setContent is passed in, make sure to call the callback on each editor state change
      setContent(JSON.stringify(convertToRaw(editorState.getCurrentContent())));
    }, [editorState]);
  }

  if (content) {
    useEffect(() => {
      // If content is passed in, set the editor state to the content initially
      setEditorState(EditorState.createWithContent(convertFromRaw(content)));
    }, [content]);
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
