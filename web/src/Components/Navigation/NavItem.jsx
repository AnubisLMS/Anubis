import React from 'react';
import clsx from 'clsx';
import {Link} from 'react-router-dom';

import makeStyles from '@material-ui/core/styles/makeStyles';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';


const useStyles = makeStyles((theme) => ({
  item: {
    'color': theme.palette.white,
    '&:hover,&:focus': {
      backgroundColor: theme.palette.dark.blue['200'],
    },
  },
  itemActiveItem: {
    color: theme.palette.primary.main,
  },
  itemPrimary: {
    fontSize: 'inherit',
  },
  itemIcon: {
    minWidth: 'auto',
    marginRight: theme.spacing(2),
  },
}));

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
      <ListItemIcon className={classes.itemIcon}>{icon}</ListItemIcon>
      <ListItemText classes={{primary: classes.itemPrimary}}>
        {childId}
      </ListItemText>
    </ListItem>
  );
}
