import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';

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

export default function BlogImg({src, alt}) {
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
}
