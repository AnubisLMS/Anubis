import React from 'react';

import Drawer from '@material-ui/core/Drawer';
import Box from '@material-ui/core/Box';
import {ReactComponent as Logo} from '../../../assets/images/Logo.svg';

import {useStyles} from './Nav.styles';

import Ad from './Ad/Ad';
import NavList from './NavList/NavList';
import PrivacyPolicy from '../PrivacyPolicy.jsx';

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
      PaperProps={{style: {scrollbarWidth: 'none'}}}
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
      <Box marginLeft="8px" marginRight="4px" marginTop="10px">
        <PrivacyPolicy/>
      </Box>

    </Drawer>
  );
};

export default Nav;
