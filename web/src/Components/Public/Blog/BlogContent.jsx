import React from 'react';
import ReactMarkdown from 'react-markdown';
import makeStyles from '@material-ui/core/styles/makeStyles';
import './markdown.css';

const useStyles = makeStyles((theme) => ({
  imgbox: {
    width: '100%',
    marginTop: theme.spacing(2),
  },
  img: {
    width: '100%',
    height: '100%',
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
  return (
    <ReactMarkdown
      escapeHtml={true}
      renderers={customRender}
    >
      {content}
    </ReactMarkdown>
  );
};

export default BlogContent;
