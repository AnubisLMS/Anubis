import React from 'react';

import {useStyles} from './Ad.styles';
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import BugReportIcon from '@material-ui/icons/BugReport';

const Ad = () => {
  const classes = useStyles();

  return (
    <Box className={classes.root}>
      <Box className={classes.iconContainer}>
        <Box className={classes.iconInnerCircle}>
          <BugReportIcon className={classes.icon} />
        </Box>
      </Box>
      <Typography className={classes.adTitle}>
        Interested in Contributing?
      </Typography>
      <Button
        className={classes.githubButton}
        component="a"
        href="https://github.com/GusSand/Anubis"
      >
        Go to our Github Repo
      </Button>
    </Box>
  );
};

export default Ad;
