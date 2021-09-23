import React from 'react';
import clsx from 'clsx';
import {Link} from 'react-router-dom';

import {useStyles} from './NavItem.styles';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';


export default function NavItem({childId, path, icon, pathname, ...props}) {
  const classes = useStyles();
  return (
    <ListItem
      button
      className={clsx(classes.item, pathname === path && classes.itemActiveItem)}
      component={Link}
      to={path}
      {...props}
    >
      <ListItemIcon
        className={clsx(classes.itemIcon, pathname === path && classes.itemActiveIcon)}
      >
        {icon}
      </ListItemIcon>
      <ListItemText classes={{primary: classes.itemPrimary}}>
        {childId}
      </ListItemText>
    </ListItem>
  );
}
