import {Divider, Typography} from '@material-ui/core';
import {Close} from '@material-ui/icons';
import Cancel from '@material-ui/icons/Cancel';
import Button from '@material-ui/core/Button';
import CheckCircle from '@material-ui/icons/CheckCircle';
import React from 'react';
import {useStyles} from './SubmissionTestExpanded.styles';

export default function SubmissionTestExpanded({
  testName,
  submissionID,
  assignmentName,
  testSuccess,
  testResult,
  onClose,
}) {
  const classes = useStyles();

  return (
    <div className={classes.submissionTestExpandedContainer}>
      <div className={classes.testHeader}>
        <Typography className={classes.testName} variant={'h5'}>
          {testName}
        </Typography>
        <Typography className={classes.submissionIDTitle}>
          Submission: <span className={classes.submissionID}>{submissionID.substr(0, 10)}</span>
        </Typography>
        <Typography className={classes.assignmentNameTitle}>
          Assignment: <span className={classes.assignmentName}>{assignmentName}</span>
        </Typography>
        <Typography className={classes.testStatus}>
          {testSuccess?
            <span className={classes.testStatusSuccess}>
              <CheckCircle className={classes.testStatusIcon} /> Test Successfully Executed
            </span>:
            <span className={classes.testStatusFail}>
              <Cancel className={classes.testStatusIcon} /> Test Execution Failed
            </span>}
        </Typography>
        <Button onClick = {() => onClose()} className={classes.closeIconWrapper} >
          <Close />
        </Button>
      </div>
      <Divider></Divider>
      <div className={classes.testBody}>
        <Typography className={classes.testOutput}>
          {testResult}
        </Typography>
      </div>
    </div>
  );
};

