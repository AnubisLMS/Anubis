import React from 'react';
import clsx from 'clsx';

import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Box';
import FiberManualRecordIcon from '@material-ui/icons/FiberManualRecord';
import QueryBuilderIcon from '@material-ui/icons/QueryBuilder';
import PersonIcon from '@material-ui/icons/Person';
import VisibilityIcon from '@material-ui/icons/Visibility';

import {toRelativeDate} from '../../../utils/datetime';

import {useStyles} from './PostListItem.styles';

export default function PostListItem({
  title,
  category,
  user,
  date,
  seenCount,
  seen = false,
  isSelected,
  handleSelect,
}) {
  const classes = useStyles();
  return (
    <Box
      onClick={handleSelect}
      className={isSelected ? clsx(classes.root, classes.selected) : classes.root}
    >
      <Box className={classes.seen}>
        <FiberManualRecordIcon className={classes.seenIcon}/>
      </Box>
      <Box className={classes.content}>
        <Typography className={classes.title}>
          {title}
        </Typography>
        <Box className={classes.secondary}>
          <Box className={classes.infoContainer}>
            <VisibilityIcon className={classes.icon} />
            <Typography>
              {seenCount}
            </Typography>
          </Box>
          <FiberManualRecordIcon className={classes.dotDivider} />
          <Box className={classes.infoContainer}>
            <QueryBuilderIcon className={classes.icon} />
            <Typography className={classes.date}>
              {toRelativeDate(new Date(date))}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};
