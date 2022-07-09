import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import React from 'react';
import RadialChart from 'react-vis/dist/radial-chart';
import {useStyles} from './SubmissionContent.styles';
import useTheme from '@mui/material/styles/useTheme';

const SubmissionContent = ({children, submission}) => {
  const classes = useStyles();
  const theme = useTheme();
  const status = {
    tests: {
      passed: submission.tests.filter((test) => test.result.passed).length,
      failed: submission.tests.filter((test) => !test.result.passed).length,
    },
    build: {
      passed: submission?.build?.passed,
    },
    all: {
      passed: submission.tests.filter((test) => (test.result.passed && test.result.output !== null)).length + (
        (!!submission?.build?.stdout && !!submission?.build?.passed) ? 1 : 0
      ),
      failed: submission.tests.filter((test) => (!test.result.passed && test.result.output !== null)).length + (
        (!!submission?.build?.stdout && !submission?.build?.passed) ? 1 : 0
      ),
      processing: submission.tests.filter((test) => test.result.output === null).length + (
        !submission?.build?.stdout ? 1 : 0
      ),
    },
  };
  const chartData = [
    {angle: status.all.failed, color: theme.palette.color.red},
    {angle: status.all.passed, color: theme.palette.color.green},
    {angle: status.all.processing, color: theme.palette.color.orange},
  ];

  return (
    <Box className={classes.submissionContainer}>
      <Box className={classes.headerContainer}>
        <RadialChart
          colorType="literal"
          radius={25}
          innerRadius={12}
          data={chartData}
          width={55}
          height={55}/>
        <Box className={classes.statusContainer}>
          <Typography className={classes.statusText}>
            {status.all.processing ? 'Tests Processing' : (
              <React.Fragment>
                {status.all.passed === submission.tests.length + 1 ?
                  'All Tests Successful' : status.all.failed === submission.tests.length + 1 ?
                    'All Tests Failed' : 'Some Tests where not Successful'}
              </React.Fragment>
            )}
          </Typography>
          <Typography className={classes.statusDescriptionText}>
            {status.all.processing ? '.'.repeat(status.all.processing) : (
              <React.Fragment>
                {status.build.passed ? '1 Successful Build' : '1 Failed Build'}
                {status.tests.passed > 0 ? `, ${status.tests.passed} Successful Tests` : ''}
                {status.tests.failed > 0 ? `, ${status.tests.failed} Failed Tests ` : ''}
              </React.Fragment>
            )}
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

