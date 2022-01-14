import React, {useEffect, useState} from 'react';
import Cookies from 'universal-cookie';
import {useSnackbar} from 'notistack';
import clsx from 'clsx';

import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import Toolbar from '@material-ui/core/Toolbar';
import Button from '@material-ui/core/Button';
import AppBar from '@material-ui/core/AppBar';
import RefreshIcon from '@material-ui/icons/Refresh';
import {Hidden} from '@material-ui/core';

import ProfileAvatar from './AccountChip/AccountChip';

export default function Header({classes, open, onDrawerToggle, user}) {
  const cookie = new Cookies();
  const {enqueueSnackbar} = useSnackbar();
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
              >
                <MenuIcon/>
              </IconButton>
            </Grid>
            <Hidden xsDown>
              <Grid item xs/>
            </Hidden>
            <Grid item>
              <div style={{display: 'flex', flexDirection: 'row'}}>
                {netid && <ProfileAvatar user={user} netid={netid} onContextChange={onContextChange} course={course}/>}
              </div>
            </Grid>
          </Grid>
        </Toolbar>
      </AppBar>
    </React.Fragment>
  );
}
