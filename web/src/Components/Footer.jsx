import Copyright from './Copyright';
import React from 'react';
import {makeStyles} from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  footer: {
    padding: theme.spacing(2),
    bottom: '0',
    left: '0',
    textAlign: 'center',
    position: 'fixed',
    height: '50px',
    width: '100%',
  },
}));

export default function Footer(props) {
  const classes = useStyles();

  return (
    <footer className={classes.footer} {...props}>
      {window.location.pathname !== '/about' ?
        <Copyright/> :
        null}
    </footer>
  );
}
