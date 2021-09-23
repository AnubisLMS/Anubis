import React, {useState} from 'react';

import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import ExitToAppOutlinedIcon from '@material-ui/icons/ExitToAppOutlined';
import LaunchOutlinedIcon from '@material-ui/icons/LaunchOutlined';

import {useStyles} from './NavList.styles';
import AuthContext from '../../../Contexts/AuthContext';
import NavItem from '../NavItem/NavItem';
import {admin_nav, footer_nav, public_nav} from '../../../navconfig';

const NavList = ({open, handleDrawerClose}) => {
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
      <List disablePadding className={classes.root}>
        {public_nav.map(({id, children}) => (
          <React.Fragment key={`${id}-thing`}>
            <ListItem className={classes.categoryHeader}>
              <ListItemText classes ={{primary: classes.categoryHeaderText}}>
                LEARNING
              </ListItemText>
            </ListItem>
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
          </React.Fragment>
        ))}
        <AuthContext.Consumer>
          {(user) => (
            <React.Fragment>
              {user && user.is_admin ? (
                <React.Fragment>
                  <ListItem className={classes.categoryHeader}>
                    <ListItemText classes ={{primary: classes.categoryHeaderText}}>
                      ADMIN
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
                </React.Fragment>
              ) : null}
            </React.Fragment>
          )}
        </AuthContext.Consumer>
      </List>
      <div className={classes.bottomPush}>
        <List>
          <ListItem className={classes.categoryHeader}>
            <ListItemText classes ={{primary: classes.categoryHeaderText}}>
              OPTIONS
            </ListItemText>
          </ListItem>
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
        </List>
      </div>
    </div>
  );
};

export default NavList;

