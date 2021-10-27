import {Button, Divider, Modal, Typography, Box} from '@material-ui/core';
import {Close} from '@material-ui/icons';
import Cancel from '@material-ui/icons/Cancel';
import CheckCircle from '@material-ui/icons/CheckCircle';
import React from 'react';
import {useStyles} from './SubmissionTestExpanded.styles';

export default function SubmissionTestExpanded({
  handleClose,
  showModal,
  testName,
  submissionID,
  assignmentName,
  testSuccess,
  testExpectedOutput,
  testActualOutput,
}) {
  const classes = useStyles();

  return (
    <Modal
      open={showModal}
      onClose={handleClose}
      aria-labelledby="modal-modal-title"
      aria-describedby="modal-modal-description"
    >
      <Box className={classes.root}>
        <div className={classes.submissionTestExpandedContainer}>
          <div className={classes.testHeader}>
            <Typography id="modal-modal-title" className={classes.testName} variant={'h5'}>
              {testName}
            </Typography>
            <Typography className={classes.submissionIDTitle}>
              Submission: <span className={classes.submissionID}>{submissionID}</span>
            </Typography>
            <Typography className={classes.assignmentNameTitle}>
              Assignment: <span className={classes.assignmentName}>{assignmentName}</span>
            </Typography>
            <Typography id="modal-modal-description" className={classes.testStatus}>
              {testSuccess?
                <span className={classes.testStatusSuccess}>
                  <CheckCircle className={classes.testStatusIcon} /> Test Successfully Executed
                </span>:
                <span className={classes.testStatusFail}>
                  <Cancel className={classes.testStatusIcon} /> Test Execution Failed
                </span>}
            </Typography>
            <Button onClick={handleClose}>
              <Typography className={classes.closeIconWrapper}><Close /></Typography>
            </Button>
          </div>
          <Divider></Divider>
          <div className={classes.testBody}>
            <Typography className={classes.testOutputTitle}>
              Expected Result:
            </Typography>
            <Typography className={classes.testOutput}>
              {testExpectedOutput}
            </Typography>
            <Typography className={classes.testOutputTitle}>
              Actual Result:
            </Typography>
            <Typography className={classes.testOutput}>
              {testActualOutput}
            </Typography>
          </div>
        </div>
      </Box>
    </Modal>
  );
};

