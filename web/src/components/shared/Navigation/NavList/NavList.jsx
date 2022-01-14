import React, {useState} from 'react';

import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';

import {useStyles} from './NavList.styles';
import AuthContext from '../../../../context/AuthContext';
import NavItem from '../NavItem/NavItem';
import {admin_nav, footer_nav, public_nav, super_nav} from '../../../../navconfig';

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
              <ListItemText classes={{primary: classes.categoryHeaderText}}>
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
              {user?.is_admin && (
                <React.Fragment>
                  <ListItem className={classes.categoryHeader}>
                    <ListItemText classes={{primary: classes.categoryHeaderText}}>
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
              )}
              {user?.is_superuser && (
                <React.Fragment>
                  <ListItem className={classes.categoryHeader}>
                    <ListItemText
                      classes={{
                        primary: classes.categoryHeaderPrimary,
                      }}
                    >
                      SUPER
                    </ListItemText>
                  </ListItem>
                  {super_nav.map(({id: childId, icon, path}) => (
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
              )}
            </React.Fragment>
          )}
        </AuthContext.Consumer>
      </List>
      <div className={classes.bottomPush}>
        <List>
          <ListItem className={classes.categoryHeader}>
            <ListItemText classes={{primary: classes.categoryHeaderText}}>
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

