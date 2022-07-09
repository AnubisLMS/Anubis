import React from 'react';
import clsx from 'clsx';

import {useStyles} from './NavItem.styles';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';


export default function NavItem({childId, path, icon, pathname, ...props}) {
  const classes = useStyles();
  return (
    <ListItem
      button
      className={clsx(classes.item, pathname === path && classes.itemActiveItem)}
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
