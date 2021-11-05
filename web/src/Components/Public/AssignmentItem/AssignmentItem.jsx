import React from 'react';
import {useHistory} from 'react-router-dom';

import AssignmentOutlinedIcon from '@material-ui/icons/AssignmentOutlined';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Item from '../Shared/Item/Item';
import {useStyles} from './AssignmentItem.styles';

const AssignmentItem = ({
  name,
  course,
  id,
  submitted,
  dueDate,
}) => {
  const history = useHistory();
  const classes = useStyles();

  return (
    <Item
      showStatus={false}
      title={name}
      subTitle={`from: ${course.name}`}
      titleIcon={<AssignmentOutlinedIcon/>}
      link={`/courses/assignment?assignmentId=${id}`}
    >
      <Typography className={submitted ? classes.green : classes.red}>
        {submitted ? 'Submitted' : 'Not Submitted'}
      </Typography>
      <Typography>Due Date: {dueDate}</Typography>
      <Button onClick={() => history.push(`/courses/assignment?assignmentId=${id}`)}>
        View Assignment
      </Button>
    </Item>
  );
};

export default AssignmentItem;
