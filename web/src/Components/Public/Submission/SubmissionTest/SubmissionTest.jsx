import React from 'react';
import {useStyles} from './SubmissionTest.styles';
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import clsx from 'clsx';
import FiberManualRecordIcon from '@material-ui/icons/FiberManualRecord';
const SubmissionTest = ({
}) =>{
  const classes = useStyles();
  const submission = {
    name: 'Test1',
    success: true,
  };
  return (
    <Box
      className={classes.root}
    >
      <Box
        className={classes.title}
      >
        <Typography
          className={classes.iconWrapper}
        >
          <FiberManualRecordIcon className={clsx(classes.circleIcon,
            submission.success ? classes.success : classes.error)}/>
        </Typography>

        <Typography
          className={classes.name}
        >
          {submission.name}
        </Typography>
        <Typography
          className={clsx(classes.testStatus, submission.success ? classes.success : classes.error)}
        >
          {submission.success ? 'Successful' : 'Failed'}
        </Typography>
      </Box>
      <Typography className={classes.expand}>
            Expand
      </Typography>
    </Box>

  );
};

export default SubmissionTest;
