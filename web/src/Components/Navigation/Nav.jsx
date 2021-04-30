import React from 'react';
import Drawer from '@material-ui/core/Drawer';
import Typography from '@material-ui/core/Typography';

import NavList from './NavList';

export default function Nav({classes, open, handleDrawerClose}) {
  return (
    <Drawer
      className={classes.drawer}
      variant="persistent"
      anchor="left"
      open={open}
      classes={{
        paper: classes.drawerPaper,
      }}
    >
      <div className={classes.drawerHeader}>
        <Typography variant={'h6'} style={{marginRight: 'auto'}}>
          Anubis
        </Typography>
      </div>
      <NavList
        variant="temporary"
        open={open}
        handleDrawerClose={handleDrawerClose}
      />
    </Drawer>
  );
}
