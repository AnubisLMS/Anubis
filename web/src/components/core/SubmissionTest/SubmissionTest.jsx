import React from 'react';
import {useStyles} from './SubmissionTest.styles';
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import clsx from 'clsx';
import FiberManualRecordIcon from '@material-ui/icons/FiberManualRecord';


const SubmissionTest = ({test, expandModal, hasExpand = true}) => {
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
        <Typography
          className={clsx(classes.testStatus, test.result.output === null ? classes.processing : (
            test.result.passed === true ? classes.success : classes.error
          ))}
        >
          {test.result.output === null ? 'Processing' : (
            test.result.passed === true ? 'Successful' : 'Failed'
          )}
        </Typography>
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
