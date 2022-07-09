import React from 'react';
import {useStyles} from './SubmissionTest.styles';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import clsx from 'clsx';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';


const SubmissionTest = ({test, expandModal, processing, hasExpand = true}) => {
  const classes = useStyles();
  return (
    <Box className={classes.root}>
      <Box className={classes.title}>
        <FiberManualRecordIcon className={clsx(classes.circleIcon,
          test.result.output === null ? classes.processing : (
            test.result.passed === true ? classes.success : classes.error
          ),
        )}/>

        <Typography className={classes.name}>{test.test.name}</Typography>
        {!!processing && test.result.output === null && (
          <Typography className={clsx(classes.testStatus, classes.processing)}>
            Skipped
          </Typography>
        )}
        {!processing && test.result.output === null && (
          <Typography className={clsx(classes.testStatus, classes.processing)}>
            Processing
          </Typography>
        )}
        {test.result.output !== null && (
          <Typography
            className={clsx(classes.testStatus, test.result.passed === true ? classes.success : classes.error)}>
            {test.result.passed === true ? 'Successful' : 'Failed'}
          </Typography>
        )}
      </Box>
      {hasExpand &&
        <Button
          className={classes.expand}
          onClick={() => expandModal()}
        >
          Expand
        </Button>
      }

    </Box>
  );
};

export default SubmissionTest;
