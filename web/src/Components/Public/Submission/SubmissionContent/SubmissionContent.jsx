import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import React from 'react';
import {RadialChart} from 'react-vis';
import {useStyles} from './SubmissionContent.styles';

const SubmissionContent = ({children, submission}) => {
  const classes = useStyles();
  const status = {
    tests: {
      passed: submission.tests.filter((test) => test.result.passed).length,
      failed: submission.tests.filter((test) => !test.result.passed).length,
    },
    build: {
      passed: submission.build.passed,
    },
    all: {
      passed: submission.tests.filter((test) => test.result.passed).length +
      (submission.build.passed ? 1 : 0),
      failed: submission.tests.filter((test) => !test.result.passed).length +
        (!submission.build.passed ? 1 : 0),
    },
  };
  const chartData = status.all.failed ? (status.all.passed ?
    [{angle: status.all.failed, color: '#FA7970'}, {angle: status.all.passed, color: '#7CE38B'}]:
    [{angle: status.all.failed, color: '#FA7970'}]) :
    [{angle: status.all.passed, color: '#7CE38B'}];

  return (
    <Box className={classes.submissionContainer}>
      <Box className={classes.headerContainer}>
        <RadialChart
          colorType="literal"
          radius={25}
          innerRadius={12}
          data={chartData}
          width={55}
          height={55} />
        <Box className={classes.statusContainer}>
          <Typography className={classes.statusText}>
            {status.all.passed === submission.tests.length + 1 ?
              'All Tests Successful' : status.all.failed === submission.tests.length + 1 ?
                'All Tests Failed': 'Some Tests where not Successful'
            }
          </Typography>
          <Typography className={classes.statusDescriptionText}>
            {status.build.passed ? '1 Successful Build, ' : '1 Failed Build, '}
            {status.tests.passed > 0 ? `${status.tests.passed} Successful Tests` : ''}
            {status.tests.failed > 0 ? `, ${status.tests.failed} Failed Tests `: ''}
          </Typography>
        </Box>
      </Box>
      <Box className={classes.testListContainer}>
        {children}
      </Box>
    </Box>
  );
};

export default SubmissionContent;

