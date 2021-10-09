
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import React from 'react';
import {RadialChart} from 'react-vis';
import {useStyles} from './SubmissionContent.styles';

export default function SubmissionContent({submission, regrade, stop}) {
  const classes = useStyles();
  const testsPassed = submission.tests.filter((test) => test.result.passed).length;
  const testsFailed = submission.tests.filter((test) => !(test.result.passed)).length;
  const totalFails = testsFailed + (submission.build.passed ? 0 : 1);
  const totalPass = testsPassed + (submission.build.passed ? 1 : 0);
  const myData = totalFails ? (totalPass ?
    [{angle: totalFails, color: '#FA7970'}, {angle: totalPass, color: '#7CE38B'}]:
    [{angle: totalFails, color: '#FA7970'}]) :
    [{angle: totalPass, color: '#7CE38B'}];

  return (
    <Box className={classes.submissionContainer}>
      <Box className={classes.headerContainer}>
        <RadialChart
          colorType="literal"
          radius={29}
          innerRadius={15}
          data={myData}
          width={60}
          height={60} />
        <Box>
          <Typography className={classes.failedContainer}>      {totalFails}   Failed
          </Typography>
          <Typography className={classes.statsContainer}>
            {submission.build.passed ? '1 successful build, ' :'1 failed build,  '}
            {testsFailed == 1 ? '1 failed test ' : (testsFailed+' failed tests ')}
            and {testsPassed == 1 ? '1 successful test' : (testsPassed+' successful tests')}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}

