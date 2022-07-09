import Copyright from './Copyright';
import React from 'react';
import {makeStyles} from '@mui/material/styles';
import {Route, Switch} from 'react-router-dom';

const useStyles = makeStyles((theme) => ({
  footer: {
    paddingBottom: theme.spacing(2),
    bottom: '0',
    left: '0',
    textAlign: 'center',
    position: 'fixed',
    height: '30px',
    width: '100%',
  },
}));

export default function Footer(props) {
  const classes = useStyles();

  return (
    <footer className={classes.footer} {...props}>
      <Switch>
        <Route exact path={'/about'}/>
        <Route>
          <Copyright/>
        </Route>
      </Switch>
    </footer>
  );
}
