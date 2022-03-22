import React from 'react';
import {useHistory} from 'react-router-dom';

import AssignmentOutlinedIcon from '@material-ui/icons/AssignmentOutlined';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Item from '../../shared/Item/Item';
import {useStyles} from './AssignmentItem.styles';
import {VisibilityOff} from '@material-ui/icons';
import {Tooltip} from '@material-ui/core';

const AssignmentItem = ({
  name,
  course,
  id,
  submitted,
  dueDate,
  visible_to_students,
}) => {
  const history = useHistory();
  const classes = useStyles();

  return (
    <Item
      showStatus={false}
      title={name}
      subTitle={`from: ${course.name}`}
      titleIcon={visible_to_students ? <Tooltip title={'Visible to students.'}><AssignmentOutlinedIcon/></Tooltip> :
        <Tooltip title={'Not visible to students.'}><VisibilityOff className={classes.red}/></Tooltip>}
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
