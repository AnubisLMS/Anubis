import React, {lazy, Suspense} from 'react';
import {Switch, Route} from 'react-router-dom';

import Forum from '../../pages/forums/Forum/Forum';

export default function Forums({user}) {
  return (
    <Switch>
      <Route exact={true} path={'/forums'}>
        <Forum user={user}/>
      </Route>
    </Switch>
  );
}

