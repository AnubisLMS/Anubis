import React, {useState} from 'react';
import Box from '@mui/material/Box';
import {makeStyles} from '@mui/styles';
import {CssBaseline} from '@mui/material';
import FormatBoldIcon from '@mui/icons-material/FormatBold';
import FormatItalicIcon from '@mui/icons-material/FormatItalic';
import FormatUnderlinedIcon from '@mui/icons-material/FormatUnderlined';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered';
import CodeIcon from '@mui/icons-material/Code';
import ImageIcon from '@mui/icons-material/Image'; // Need draft-js plugin
import IconButton from '@mui/material/IconButton';


import {RichUtils} from 'draft-js';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'flex-start',
    alignItems: 'center',
    padding: theme.spacing(0),
    margin: theme.spacing(0.5, 0.25),
  },
  p: {
    margin: theme.spacing(0),
  },
  buttonIcon: {
    // margin: theme.spacing(1, 0, 0, 0),
  },
  IconLogo: {
    // margin: theme.spacing(0, 0, 0, 0),
    translate: 'transform(-50%, -50%)',
    padding: theme.spacing(0.1),
  },
  //   inline: {
  //     display: 'inline',
  //   },
  //   datePicker: {
  //     width: 300,
  //     marginRight: theme.spacing(2),
  //   },
  //   button: {
  //     marginRight: theme.spacing(1),
  //   },
}));

export default function EditorToolbar({editorState, setEditorState}) {
  const classes = useStyles();
  // Create JSON array of the icon and their functions FIX THIS
  const tools = [
    {label: 'H1', style: 'header-one', method: 'block'},
    {label: 'H2', style: 'header-two', method: 'block'},
    {label: 'H3', style: 'header-three', method: 'block'},
    {
      label: 'bold',
      style: 'BOLD',
      icon: <FormatBoldIcon className={classes.IconLogo} />,
      method: 'inline', // Convert to enum?
    },
    {
      label: 'italic',
      style: 'ITALIC',
      icon: <FormatItalicIcon className={classes.IconLogo} />,
      method: 'inline',
    },
    {
      label: 'underline',
      style: 'UNDERLINE',
      icon: <FormatUnderlinedIcon className={classes.IconLogo} />,
      method: 'inline',
    },
    // {
    //   label: 'Blockquote',
    //   style: 'blockQuote',
    //   icon: <FormatQuoteIcon className={classes.IconLogo} />,
    //   method: 'block',
    // },
    {
      label: 'Unordered-List',
      style: 'unordered-list-item',
      method: 'block',
      icon: <FormatListBulletedIcon className={classes.IconLogo} />,
    },
    {
      label: 'Ordered-List',
      style: 'ordered-list-item',
      method: 'block',
      icon: <FormatListNumberedIcon className={classes.IconLogo} />,
    },
    // {
    //   label: 'Code Block',
    //   style: 'CODEBLOCK',
    //   icon: <CodeIcon className={classes.IconLogo} />,
    //   method: 'inline',
    // },
    // {
    //   label: 'Uppercase',
    //   style: 'UPPERCASE',
    //   method: 'inline',
    // },
    // {
    //   label: 'lowercase',
    //   style: 'LOWERCASE',
    //   method: 'inline',
    // },
  ];
  const applyStyle = (e, style, method) => {
    e.preventDefault();
    (method === 'block') ? setEditorState(RichUtils.toggleBlockType(editorState, style)) :
      setEditorState(RichUtils.toggleInlineStyle(editorState, style));
  };

  const isActive = (style, method) => {
    if (method === 'block') {
      const selection = editorState.getSelection();
      const blockType = editorState
        .getCurrentContent()
        .getBlockForKey(selection.getStartKey())
        .getType();
      return blockType === style;
    } else {
      const currentStyle = editorState.getCurrentInlineStyle();
      return currentStyle.has(style);
    }
  };

  return (
    <>
      <CssBaseline />
      <Box className={classes.root}>
        {tools.map((tool, id) => (
          <Box
            key={tool.label}
          >
            <IconButton
              color= {isActive(tool.style, tool.method) ? 'primary' : 'inherit'}
              className={classes.buttonIcon}
              key={id}
              size="small"
              onClick={(e) => applyStyle(e, tool.style, tool.method)}
              onMouseDown={(e) => e.preventDefault()}
            >
              {/* If the tool has an icon, render it if not render the label */}
              {tool.icon || tool.label}
            </IconButton>
          </Box>
        ))}
      </Box>
    </>
  );
};
