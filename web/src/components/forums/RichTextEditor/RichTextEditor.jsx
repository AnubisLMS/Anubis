import React, {useState, useRef} from 'react';
import {EditorState, RichUtils, convertToRaw} from 'draft-js';
import Editor, {composeDecorators} from '@draft-js-plugins/editor';
import createResizablePlugin from '@draft-js-plugins/resizeable';
import EditorToolbar from './Toolbar/EditorToolbar';
import createImagePlugin from '@draft-js-plugins/image';
import {makeStyles} from '@mui/styles';
import 'draft-js/dist/Draft.css';
import './TextEditor.css';
const resizeablePlugin = createResizablePlugin();
const decorator = composeDecorators(
  resizeablePlugin.decorator,
);
const imagePlugin = createImagePlugin({decorator});

const useStyles = makeStyles((theme) => ({
  toolbarContainer: {
    borderColor: theme.palette.white,
    borderTop: theme.spacing(0.1) + ' solid',
    borderBottom: theme.spacing(0.1) + ' solid',
  },
}));

export default function RichTextEditor({getContent}) {
  const [editorState, setEditorState] = useState(EditorState.createEmpty());
  const editor = useRef(null);
  const classes = useStyles();
  getContent = () => {
    return JSON.stringify(convertToRaw(editorState.getCurrentContent()));
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
    <>
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
    </>
  );
};
