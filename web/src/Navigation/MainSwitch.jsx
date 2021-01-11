import React from 'react';
import {Route, Switch} from 'react-router-dom';
import {footerconfig, navconfig} from './navconfig';
import Grid from '@material-ui/core/Grid';

export default function MainSwitch() {
  return (
    <Switch>
      {navconfig.map(({children}) => children.map(({path, Page = 'div'}) => (
        <Route exact path={path} key={path}>
          <Grid container spacing={2} justify="center" alignItems="center">
            <Page/>
          </Grid>
        </Route>
      )))}
      {footerconfig.map(({path, Page}) => (
        <Route exact path={path} key={`path-${path}`}>
          <Grid container spacing={2} justify="center" alignItems="center">
            <Page/>
          </Grid>
        </Route>
      ))}
      <Route>
        404 not found
      </Route>
    </Switch>
  );
}
