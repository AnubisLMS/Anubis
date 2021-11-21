import React from 'react';
import {Redirect, Route, Switch} from 'react-router-dom';
import {public_nav, admin_nav, super_nav, footer_nav, not_shown_nav} from './navconfig';
import NotFound from './Components/NotFound';

export default function Main({user}) {
  return (
    <Switch>
      {public_nav.map(({children}) => children.map(({path, Page, exact = true}) => (
        <Route exact={exact} path={path} key={path}>
          <Page/>
        </Route>
      )))}
      {footer_nav.map(({path, Page, exact = true}) => (
        <Route exact={exact} path={path} key={`path-${path}`}>
          <Page/>
        </Route>
      ))}
      {admin_nav.map(({path, Page, exact = true}) => (
        <Route exact={exact} path={path} key={`path-${path}`}>
          {user?.is_admin && (
            <Page/>
          )}
        </Route>
      ))}
      {super_nav.map(({path, Page, exact = true}) => (
        <Route exact={exact} path={path} key={`path-${path}`}>
          {user?.is_superuser && (
            <Page/>
          )}
        </Route>
      ))}
      {not_shown_nav.map(({path, Page, exact = true}) => (
        <Route exact={exact} path={path} key={`path-${path}`}>
          <Page/>
        </Route>
      ))}
      <Route exact path={'/'}>
        <Redirect to={'/about'}/>
      </Route>
      <Route>
        <NotFound/>
      </Route>
    </Switch>
  );
}
