import React from 'react';
import clsx from 'clsx';
import {makeStyles} from '@material-ui/core/styles';
import Divider from '@material-ui/core/Divider';
import Drawer from '@material-ui/core/Drawer';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import HomeIcon from '@material-ui/icons/Home';
import {Link} from 'react-router-dom';

import {footerconfig, navconfig} from './navconfig';
import ExitToAppOutlinedIcon from '@material-ui/icons/ExitToAppOutlined';
import LaunchOutlinedIcon from '@material-ui/icons/LaunchOutlined';

const useStyles = makeStyles((theme) => ({
  categoryHeader: {
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
  },
  categoryHeaderPrimary: {
    color: theme.palette.common.white,
  },
  item: {
    'paddingTop': 1,
    'paddingBottom': 1,
    'color': 'rgba(255, 255, 255, 0.7)',
    '&:hover,&:focus': {
      backgroundColor: 'rgba(255, 255, 255, 0.08)',
    },
  },
  itemCategory: {
    backgroundColor: '#232f3e',
    boxShadow: '0 -1px 0 #404854 inset',
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
  },
  firebase: {
    fontSize: 24,
    color: theme.palette.common.white,
  },
  itemActiveItem: {
    color: '#4fc3f7',
  },
  itemPrimary: {
    fontSize: 'inherit',
  },
  itemIcon: {
    minWidth: 'auto',
    marginRight: theme.spacing(2),
  },
  divider: {
    marginTop: theme.spacing(2),
  },
}));


export default function NavList({...other}) {
  const classes = useStyles();

  return (
    <Drawer variant="permanent" {...other}>
      <List disablePadding>
        <ListItem className={clsx(classes.firebase, classes.item, classes.itemCategory)} key={0}>
          Anubis
        </ListItem>
        <ListItem className={clsx(classes.item, classes.itemCategory)} key={1}>
          <ListItemIcon className={classes.itemIcon}>
            <HomeIcon/>
          </ListItemIcon>
          <ListItemText
            classes={{
              primary: classes.itemPrimary,
            }}
          >
            Anubis
          </ListItemText>
        </ListItem>
        {navconfig.map(({id, children}) => (
          <React.Fragment key={`${id}-thing`}>
            <ListItem className={classes.categoryHeader}>
              <ListItemText
                classes={{
                  primary: classes.categoryHeaderPrimary,
                }}
              >
                {id}
              </ListItemText>
            </ListItem>
            {children.map(({id: childId, icon, path}) => (
              <ListItem
                key={childId}
                button
                className={clsx(classes.item, window.location.pathname === path && classes.itemActiveItem)}
                component={Link}
                to={path}
              >
                <ListItemIcon className={classes.itemIcon}>{icon}</ListItemIcon>
                <ListItemText
                  classes={{
                    primary: classes.itemPrimary,
                  }}
                >
                  {childId}
                </ListItemText>
              </ListItem>
            ))}

            <Divider className={classes.divider}/>
          </React.Fragment>
        ))}
      </List>
      <div className={classes.bottomPush}>
        <List>
          {footerconfig.map(({id, icon, path}) => (
            <ListItem
              button key={id}
              component={Link}
              to={path}
              selected={window.location.pathname === path}
            >
              <ListItemIcon>{icon}</ListItemIcon>
              <ListItemText primary={id}/>
            </ListItem>
          ))}
          <ListItem
            button key="Login"
            component={'a'}
            href={'/api/public/auth/login'}
          >
            <ListItemIcon><ExitToAppOutlinedIcon/></ListItemIcon>
            <ListItemText primary={'Login'}/>
          </ListItem>
          <ListItem
            button key="Logout"
            component={'a'}
            href={'/api/public/auth/logout'}
          >
            <ListItemIcon><LaunchOutlinedIcon/></ListItemIcon>
            <ListItemText primary={'Logout'}/>
          </ListItem>
        </List>
      </div>
    </Drawer>
  );
}
