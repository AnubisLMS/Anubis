import React from 'react';
import {useHistory} from 'react-router-dom';

import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Item from '../../shared/Item/Item';
import {useStyles} from './AssignmentItem.styles';
import {VisibilityOff} from '@mui/icons-material';
import Tooltip from '@mui/material/Tooltip';

const AssignmentItem = ({
  name,
  course,
  id,
  submitted,
  dueDate,
  visible_to_students,
  complete,
  shellAutograde,
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
      {shellAutograde ? (
        <Typography className={!submitted ? classes.red : (
          complete ? classes.green : classes.orange
        )}>
          {!submitted ? 'Not Started' : (
            complete ? 'Complete' : 'Incomplete'
          )}
        </Typography>
      ) : (
        <Typography className={submitted ? classes.green : classes.red}>
          {submitted ? 'Submitted' : 'Not Started'}
        </Typography>
      )}
      <Typography>Due Date: {dueDate}</Typography>
      <Button
        color={'primary'}
        variant={'contained'}
        onClick={() => history.push(`/courses/assignment?assignmentId=${id}`)}
      >
        View Assignment
      </Button>
    </Item>
  );
};

export default AssignmentItem;
