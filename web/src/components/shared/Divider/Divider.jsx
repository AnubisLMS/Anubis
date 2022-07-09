import React from 'react';

import Box from '@mui/material/Box';
import {useStyles} from './Divider.styles';

const Divider = () => {
  const classes = useStyles();
  return (
    <Box className={classes.divider} />
  );
};

export default Divider;
