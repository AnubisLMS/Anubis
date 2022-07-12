import React from 'react';
import AboutRedirect from './components/shared/AboutRedirect';
import {Redirect, Route, Switch} from 'react-router-dom';
import {public_nav, admin_nav, super_nav, footer_nav, not_shown_nav} from './navconfig';

import NotFound from './components/shared/NotFound';

export default function Main({user}) {
  if (user === undefined) {
    return null;
  }
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
      <Route exact path={'/about'}>
        <AboutRedirect user={user}/>
      </Route>
      <Route exact path={'/'}>
        {user === null ? <Redirect to={'/about'}/> : <Redirect to={'/visuals'}/>}
      </Route>
      <Route>
        <NotFound/>
      </Route>
    </Switch>
  );
}
