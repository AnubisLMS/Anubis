import React from 'react';

import Button from '@material-ui/core/Button';
import Drawer from '@material-ui/core/Drawer';
import Typography from '@material-ui/core/Typography';
import GitHubIcon from '@material-ui/icons/GitHub';

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
      style={{height: '100%'}}
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
      <div style={{display: 'flex', flexDirection: 'column-reverse', height: '100%'}}>
        <div style={{display: 'flex', justifyContent: 'center', marginTop: '10px'}}>
          <Button
            variant="contained"
            color="primary"
            className={classes.githubButton}
            startIcon={<GitHubIcon size="small"/>}
            component="a"
            href="https://github.com/AnubisLMS/Anubis"
            target="_blank"
            rel="noreferrer"
            size="small"
          >
            We&apos;re on Github
          </Button>
        </div>
      </div>
    </Drawer>
  );
}
