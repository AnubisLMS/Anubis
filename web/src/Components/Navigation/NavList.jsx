import React, {useState} from 'react';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Divider from '@material-ui/core/Divider';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import ExitToAppOutlinedIcon from '@material-ui/icons/ExitToAppOutlined';
import LaunchOutlinedIcon from '@material-ui/icons/LaunchOutlined';

import AuthContext from '../../Contexts/AuthContext';
import NavItem from './NavItem';
import {admin_nav, footer_nav, public_nav} from '../../navconfig';

const useStyles = makeStyles((theme) => ({
  categoryHeader: {
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
  },
  categoryHeaderPrimary: {
    color: theme.palette.common.white,
  },
  item: {
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
    color: theme.palette.white,
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


export default function NavList({open, handleDrawerClose}) {
  const classes = useStyles();
  const [pathname, setPathname] = useState(window.location.pathname);
  const onClickWrap = (func) => () => {
    func();
    // 960px is the size of md
    if (open && window.innerWidth < 960) {
      handleDrawerClose();
    }
  };

  return (
    <div>
      <List disablePadding>
        {public_nav.map(({id, children}) => (
          <React.Fragment key={`${id}-thing`}>
            {children.map(({id: childId, icon, path}) => (
              <NavItem
                key={childId}
                onClick={onClickWrap(() => setPathname(path))}
                childId={childId}
                icon={icon}
                path={path}
                pathname={pathname}
              />
            ))}
            <Divider className={classes.divider}/>
          </React.Fragment>
        ))}
        <AuthContext.Consumer>
          {(user) => (
            <React.Fragment>
              {user && user.is_admin ? (
                <React.Fragment>
                  <ListItem className={classes.categoryHeader}>
                    <ListItemText
                      classes={{
                        primary: classes.categoryHeaderPrimary,
                      }}
                    >
                      Admin
                    </ListItemText>
                  </ListItem>
                  {admin_nav.map(({id: childId, icon, path}) => (
                    <NavItem
                      key={childId}
                      onClick={onClickWrap(() => setPathname(path))}
                      childId={childId}
                      icon={icon}
                      path={path}
                      pathname={pathname}
                    />
                  ))}
                  <Divider className={classes.divider}/>
                </React.Fragment>
              ) : null}
            </React.Fragment>
          )}
        </AuthContext.Consumer>
      </List>
      <div className={classes.bottomPush}>
        <List>
          {footer_nav.map(({id: childId, icon, path}) => (
            <NavItem
              key={childId}
              onClick={onClickWrap(() => setPathname(path))}
              childId={childId}
              icon={icon}
              path={path}
              pathname={pathname}
            />
          ))}
          <ListItem
            button
            component={'a'}
            href={'/api/public/auth/login'}
            className={classes.item}
          >
            <ListItemIcon><ExitToAppOutlinedIcon/></ListItemIcon>
            <ListItemText primary={'Login'}/>
          </ListItem>
          <ListItem
            button
            className={classes.item}
            component={'a'}
            href={'/api/public/auth/logout'}
          >
            <ListItemIcon><LaunchOutlinedIcon/></ListItemIcon>
            <ListItemText primary={'Logout'}/>
          </ListItem>
        </List>
      </div>
    </div>
  );
}
