import React from 'react';
import clsx from 'clsx';

import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Box';
import FiberManualRecordIcon from '@material-ui/icons/FiberManualRecord';

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
          <Typography>
            {user}
          </Typography>
          <p>
            -
          </p>
          <Typography>
            {category}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};
