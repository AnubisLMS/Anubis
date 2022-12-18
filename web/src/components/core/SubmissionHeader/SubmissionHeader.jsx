import React, {Fragment} from 'react';

import {Box} from '@mui/material';
import {Typography} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import RefreshIcon from '@mui/icons-material/Refresh';

import clsx from 'clsx';
import {useStyles} from './SubmissionHeader.styles';
import Button from '@mui/material/Button';


const SubmissionHeader = ({
  assignment_name,
  timestamp,
  id,
  commit,
  on_time,
  state,
  processed,
  regrade,
})=> {
  const classes = useStyles();
  const DATE_OPTIONS = {weekday: 'long', year: 'numeric', month: 'short', day: 'numeric'};

  return (
    <Box className = {classes.submissionSummaryContainer}>
      <Box className={classes.dataContainer}>
        <Typography className={classes.assignmentName}>{assignment_name}</Typography>
        {!commit.startsWith('fake-') && (
          <Fragment>
            <Typography className={classes.textLabel}>{'Submission: '}</Typography>
            <Typography className={classes.textContent}>{commit.substring(0, 20)}</Typography>
          </Fragment>
        )}
        <Typography className={classes.textLabel}>{'Submitted: '}</Typography>
        <Typography className={classes.textContent}>
          {new Date(timestamp).toLocaleDateString('en-US', DATE_OPTIONS)}
        </Typography>
        <Typography className={classes.textLabel}>{'State: '}</Typography>
        <Typography className={classes.textContent}>
          {state}
        </Typography>
      </Box>
      <Box className={classes.dataContainer}>
        {!commit.startsWith('fake-') && (
          <Button
            variant={'contained'}
            color={'primary'}
            startIcon={<RefreshIcon/>}
            className={clsx(classes.dataItem)}
            disabled={!processed}
            onClick={regrade}
          >
            Regrade
          </Button>
        )}
        <Typography className={clsx(classes.dataItem, classes.circleIcon, on_time ? classes.success : classes.error)}>
          { on_time ? <CheckCircleIcon/> : <CancelIcon/>}
        </Typography>
        <Typography className={clsx(classes.submittedStatus, on_time ? classes.success : classes.error)}>
          { on_time ? 'Submitted On Time' : 'Submitted Late'}
        </Typography>
      </Box>
    </Box>
  );
};

export default SubmissionHeader;
