import React, {useEffect, useState} from 'react';
import Cookies from 'universal-cookie';
import clsx from 'clsx';

import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Toolbar from '@mui/material/Toolbar';
import AppBar from '@mui/material/AppBar';
import Hidden from '@mui/material/Hidden';
import Button from '@mui/material/Button';

import ProfileAvatar from './AccountChip/AccountChip';

export default function Header({classes, open, onDrawerToggle, user}) {
  const cookie = new Cookies();
  const [netid, setNetid] = useState(null);
  const [course, setCourse] = useState((() => {
    try {
      return JSON.parse(atob(cookie.get('course')));
    } catch (_) {
    }
    return null;
  })());

  useEffect(() => {
    if ((user?.admin_for?.length ?? 0) > 0) {
      try {
        JSON.parse(atob(cookie.get('course')));
      } catch (_) {
        cookie.set('course', btoa(JSON.stringify(user.admin_for[0])), {path: '/'});
        setCourse(user.admin_for[0]);
      }
    }
    if (user?.netid) {
      setNetid(user.netid);
    }
  }, [user]);

  const onContextChange = (course) => {
    cookie.remove('course', {path: '/'});
    if (!!course) {
      cookie.set('course', btoa(JSON.stringify(course)), {path: '/'});
      setTimeout(() => {
        window.location.reload(0);
      }, 100);
    }
    setCourse(course);
  };

  return (
    <React.Fragment>
      <AppBar
        elevation={0}
        position="fixed"
        className={clsx(classes.appBar, {
          [classes.appBarShift]: open,
        })}
      >
        <Toolbar>
          <Grid container spacing={1} alignItems="center">
            <Grid item>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                onClick={onDrawerToggle}
                className={classes.menuButton}
                size="large">
                <MenuIcon/>
              </IconButton>
            </Grid>
            <Hidden smDown>
              <Grid item xs/>
            </Hidden>
            <Grid item>
              <div style={{display: 'flex', flexDirection: 'row'}}>
                {netid && <ProfileAvatar user={user} netid={netid} onContextChange={onContextChange} course={course}/>}
                {!netid &&
                  <a href="/api/public/auth/login">
                    <Button
                      className={classes.logInButton}
                    >
                      Log In
                    </Button>
                  </a>
                }
              </div>
            </Grid>
          </Grid>
        </Toolbar>
      </AppBar>
    </React.Fragment>
  );
}
