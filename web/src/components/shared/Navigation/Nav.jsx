import React from 'react';

import Drawer from '@mui/material/Drawer';
import Box from '@mui/material/Box';
import {ReactComponent as Logo} from '../../../assets/images/Logo.svg';

import {useStyles} from './Nav.styles';

import Ad from './Ad/Ad';
import NavList from './NavList/NavList';

const Nav = ({open, handleDrawerClose}) => {
  const classes = useStyles();
  return (
    <Drawer
      className={classes.drawer}
      variant="persistent"
      anchor="left"
      open={open}
      classes={{
        paper: classes.drawerPaper,
      }}
      style={{height: '100%'}}
    >
      <Box className={classes.listContainer}>
        <Box className={classes.logoContainer}>
          <Logo className={classes.logo}/>
        </Box>
        <NavList
          variant="temporary"
          open={open}
          handleDrawerClose={handleDrawerClose}
        />
      </Box>
      <Box marginLeft="8px" marginRight="8px" marginTop="20px">
        <Ad/>
      </Box>
    </Drawer>
  );
};

export default Nav;
