import React from 'react';

import AssessmentIcon from '@mui/icons-material/Assessment';
import Typography from '@mui/material/Typography';

import Item from '../../shared/Item/Item';
import {useStyles} from './SubmissionItem.styles';
import Tooltip from '@mui/material/Tooltip';

const SubmissionItem = ({
  assignmentDue,
  assignmentName,
  accepted,
  id,
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
      subTitle={!commit.startsWith('fake-') ? commit.substring(0, 15) : ''}
      titleIcon={<AssessmentIcon/>}
      link={`/submission/${id}`}
    >
      <Typography>
        {`${tests.filter((test) => test.result.passed).length}/${tests.length} Tests Passed`}
      </Typography>
      {accepted ? (
        <Typography
          className={timeStamp <= assignmentDue ? classes.green : classes.red}
        >
          {timeStamp <= assignmentDue ? 'Submitted On Time' : 'Submitted Late'}
        </Typography>
      ) : (
        <Tooltip title={'This assignment does not accept late submissions'}>
          <Typography
            className={classes.red}
          >
            Not Accepted
          </Typography>
        </Tooltip>
      )}
      <Typography> {new Date(timeStamp).toLocaleString()}</Typography>
    </Item>
  );
};

export default SubmissionItem;
