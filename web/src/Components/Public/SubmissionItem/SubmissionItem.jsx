import React from 'react';

import AssessmentIcon from '@material-ui/icons/Assessment';
import Typography from '@material-ui/core/Typography';

import Item from '../../Shared/Item/Item';
import {useStyles} from './SubmissionItem.styles';

const SubmissionItem = ({
  assignmentDue,
  assignmentName,
  commit,
  processed,
  tests,
  timeStamp,
}) => {
  const classes = useStyles();

  return (
    <Item
      showStatus={true}
      statusColor={processed ? 'green' : 'red'}
      title={assignmentName}
      subTitle={commit.substring(0, 15)}
      titleIcon={<AssessmentIcon/>}
      link={`/submission?commit=${commit}`}
    >
      <Typography>
        {`${tests.filter((test) => test.result.passed).length}/${tests.length} Tests Passed`}
      </Typography>
      <Typography
        className={timeStamp <= assignmentDue ? classes.green : classes.red}
      >
        {timeStamp <= assignmentDue ? 'Submitted On Time' : 'Submitted Late'}
      </Typography>
      <Typography> {new Date(timeStamp).toLocaleString()}</Typography>
    </Item>
  );
};

export default SubmissionItem;
