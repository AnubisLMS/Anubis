import React from 'react';

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import AddIcon from '@mui/icons-material/Add';

import {useStyles} from './JoinCourseItem.styles';

const JoinCourseItem = ({callback}) => {
  const classes = useStyles();
  return (
    <Box className={classes.root} onClick={callback}>
      <AddIcon />
      <Typography className={classes.text}>Join Another Course</Typography>
    </Box>
  );
};

export default JoinCourseItem;
