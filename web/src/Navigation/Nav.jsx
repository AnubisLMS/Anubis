import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Hidden from '@material-ui/core/Hidden';

import NavList from '../Components/Navigation/NavList';

const drawerWidth = 256;

const useSytles = makeStyles((theme) => ({
  drawer: {
    [theme.breakpoints.up('sm')]: {
      width: drawerWidth,
      flexShrink: 0,
    },
  },
}));

export default function Nav({open, onDrawerToggle}) {
  const classes = useSytles();

  return (
    <nav className={classes.drawer}>
      <Hidden smUp implementation="js">
        <NavList
          PaperProps={{style: {width: drawerWidth}}}
          variant="temporary"
          open={open}
          onClose={onDrawerToggle}
        />
      </Hidden>
      <Hidden xsDown implementation="css">
        <NavList PaperProps={{style: {width: drawerWidth}}}/>
      </Hidden>
    </nav>
  );
}
