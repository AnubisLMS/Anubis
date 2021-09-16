import React from 'react';

import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import AddIcon from '@material-ui/icons/Add';

import {useStyles} from './EmptyCourseCard.styles';

const EmptyCourseCard = ({callback}) => {
  const classes = useStyles();
  return (
    <Box className={classes.emptyCourseCardContainer} onClick={callback}>
      <Box textAlign="center">
        <AddIcon />
        <Typography className={classes.joinText}>Join Course</Typography>
      </Box>
    </Box>
  );
};

export default EmptyCourseCard;
