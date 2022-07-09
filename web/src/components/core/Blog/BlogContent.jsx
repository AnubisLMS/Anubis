import React from 'react';
import ReactMarkdown from 'react-markdown';
import makeStyles from '@mui/styles/makeStyles';

const useStyles = makeStyles((theme) => ({
  imgbox: {
    width: '100%',
    marginTop: theme.spacing(2),
  },
  img: {
    width: '100%',
    height: '100%',
  },
  markdown: {
    '& p': {
      fontSize: '1.1rem',
      marginBottom: '1.3rem',
    },
    '& body': {
      lineHeight: '1.85',
      fontSize: '18px',
    },
    '& h4': {
      fontSize: '1.1rem',
      opacity: .7,
    },
    '& blockquote': {
      borderLeft: '3px solid #4fc3f7',
      paddingLeft: '1rem',
    },
    '& a': {
      textDecoration: 'none',
      color: '#4fc3f7',
    },
    '& li': {
      fontSize: '1rem',
      marginBottom: '.3rem',
    },
    '& code': {
      paddingRight: '6px',
      paddingLeft: '6px',
      paddingBottom: '2px',
      paddingTop: '3px',
      backgroundColor: '#4F4F4F',
      borderRadius: '3px',
      borderBottom: '1px solid #4fc3f7',
    },
  },
}));
const customRender = {
  image: ({
    alt,
    src,
    title,
  }) => {
    const classes = useStyles();
    return (
      <div className={classes.imgbox}>
        <img
          className={classes.img}
          src={src}
          alt={alt}
        />
      </div>
    );
  },
};

const BlogContent = ({content}) => {
  const classes = useStyles();
  return (
    <ReactMarkdown
      className = {classes.markdown}
      escapeHtml={true}
      renderers={customRender}
    >
      {content}
    </ReactMarkdown>
  );
};

export default BlogContent;

