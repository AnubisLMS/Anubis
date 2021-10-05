import React from 'react';

import {Box} from '@material-ui/core';
import {Typography} from '@material-ui/core';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import CancelIcon from '@material-ui/icons/Cancel';
import green from '@material-ui/core/colors/green';
import red from '@material-ui/core/colors/red';

import clsx from 'clsx';
import {useStyles} from './SubmissionHeader.styles';


const SubmissionHeader = ({
  assignment_name,
  timestamp,
  assignment_due,
  commit,
  on_time,
})=> {
  const classes = useStyles();
  const DATE_OPTIONS = {weekday: 'long', year: 'numeric', month: 'short', day: 'numeric'};

  return (
    <Box className = {classes.submissionSummaryContainer}>
      <Box className={classes.dataContainer}>
        <Typography className={classes.assignmentName}>{assignment_name}</Typography>
        <Typography className={classes.textLabel}>{'Submission: '}</Typography>
        <Typography className={classes.textContent}>{commit} </Typography>
        <Typography className={classes.textLabel}>{'Submitted: '}</Typography>
        <Typography className={classes.textContent}>
          {new Date(timestamp).toLocaleDateString('en-US', DATE_OPTIONS)}
        </Typography>
      </Box>
      <Box className={classes.dataContainer}>
        <Typography className={classes.circleIcon}>
          { on_time ?
            <CheckCircleIcon style={{color: green[500], fontSize: 20}}/> :
            <CancelIcon style={{color: red[500], fontSize: 20}}/>
          }
        </Typography>
        <Typography
          className={clsx(classes.submittedStatus, on_time ? classes.sucess : classes.error)}
        >
          { on_time ? 'Submitted On Time' : 'Submitted Late'}
        </Typography>
      </Box>
    </Box>
    // </Box>
  );
};

export default SubmissionHeader;
