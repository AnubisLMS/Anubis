import React from 'react';

import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import AddIcon from '@material-ui/icons/Add';

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
