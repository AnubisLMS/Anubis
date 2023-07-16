import React from 'react';
import {Box, CssBaseline, IconButton} from '@mui/material';
import {
  FormatBold as FormatBoldIcon,
  FormatItalic as FormatItalicIcon,
  FormatUnderlined as FormatUnderlinedIcon,
  FormatListBulleted as FormatListBulletedIcon,
  FormatListNumbered as FormatListNumberedIcon,
} from '@mui/icons-material';
import EmbedImage from './Embed/EmbedImage';
import {useStyles} from './EditorToolbar.styles';
import {RichUtils} from 'draft-js';

const MODES = {
  INLINE: 'inline',
  BLOCK: 'block',
};

export default function EditorToolbar({editorState, setEditorState, imagePlugin}) {
  const classes = useStyles();

  // Create JSON array of the icon and their functions
  const tools = [
    {
      label: 'H1',
      style: 'header-one',
      method: MODES.BLOCK,
    },
    {
      label: 'H2',
      style: 'header-two',
      method: MODES.BLOCK,
    },
    {
      label: 'H3',
      style: 'header-three',
      method: MODES.BLOCK,
    },
    {
      label: 'bold',
      style: 'BOLD',
      icon: <FormatBoldIcon className={classes.IconLogo} />,
      method: MODES.INLINE,
    },
    {
      label: 'italic',
      style: 'ITALIC',
      icon: <FormatItalicIcon className={classes.IconLogo} />,
      method: MODES.INLINE,
    },
    {
      label: 'underline',
      style: 'UNDERLINE',
      icon: <FormatUnderlinedIcon className={classes.IconLogo} />,
      method: MODES.INLINE,
    },
    {
      label: 'unordered-list',
      style: 'unordered-list-item',
      method: MODES.BLOCK,
      icon: <FormatListBulletedIcon className={classes.IconLogo} />,
    },
    {
      label: 'ordered-list',
      style: 'ordered-list-item',
      method: MODES.BLOCK,
      icon: <FormatListNumberedIcon className={classes.IconLogo} />,
    },
  ];

  const applyStyle = (e, style, method) => {
    e.preventDefault();
    if (method === MODES.BLOCK) {
      setEditorState(RichUtils.toggleBlockType(editorState, style));
    } else if (method === MODES.INLINE) {
      setEditorState(RichUtils.toggleInlineStyle(editorState, style));
    }
  };

  const isActive = (style, method) => {
    if (method === MODES.BLOCK) {
      const selection = editorState.getSelection();
      const blockType = editorState
        .getCurrentContent()
        .getBlockForKey(selection.getStartKey())
        .getType();
      return blockType === style;
    } else if (method === MODES.INLINE) {
      const currentStyle = editorState.getCurrentInlineStyle();
      return currentStyle.has(style);
    }
  };

  const insertImage = (url) => {
    console.log('inserting image');
    setEditorState(imagePlugin.addImage(editorState, url));
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
              onClick={(e) => applyStyle(e, tool.style, tool.method)} // Open modal for image
              onMouseDown={(e) => e.preventDefault()}
            >
              {/* If the tool has an icon, render it if not render the label */}
              {tool.icon || tool.label}
            </IconButton>
          </Box>
        ))}
        <EmbedImage className={classes.IconButton} embedImage={insertImage} />
      </Box>
    </>
  );
};
