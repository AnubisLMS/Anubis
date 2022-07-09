import React from 'react';
import clsx from 'clsx';

import Box from '@mui/material/Box';
import Typography from '@mui/material/Box';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import QueryBuilderIcon from '@mui/icons-material/QueryBuilder';
import PersonIcon from '@mui/icons-material/Person';
import VisibilityIcon from '@mui/icons-material/Visibility';

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
