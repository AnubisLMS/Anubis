import React from 'react';
import clsx from 'clsx';

import AppBar from '@material-ui/core/AppBar';
import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import Toolbar from '@material-ui/core/Toolbar';
import Chip from '@material-ui/core/Chip';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import {useTheme} from '@material-ui/core/styles';


export default function Header({classes, open, onDrawerToggle, user}) {
  const theme = useTheme();

  return (
    <React.Fragment>
      <AppBar
        color="primary"
        elevation={0}
        position="fixed"
        className={clsx(classes.appBar, {
          [classes.appBarShift]: open,
        })}
      >
        <Toolbar>
          <Grid container spacing={1} alignItems="center">
            {open ? (
              <Grid item>
                <IconButton
                  onClick={onDrawerToggle}
                  aria-label="close drawer"
                >
                  {theme.direction === 'ltr' ? <ChevronLeftIcon/> : <ChevronRightIcon/>}
                </IconButton>
              </Grid>
            ) : (
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
            )}
            <Grid item xs/>
            <Grid item>
              <div className={classes.avatar}>
                <Chip clickable label={user?.netid}/>
              </div>
            </Grid>
          </Grid>
        </Toolbar>
      </AppBar>
    </React.Fragment>
  );
}
