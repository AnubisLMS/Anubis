import React from 'react';
import {useHistory} from 'react-router-dom';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import CardActionArea from '@material-ui/core/CardActionArea';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Box from '@material-ui/core/Box';
import clsx from 'clsx';

import {useStyles} from './AssignmentCardV2.styles';


const AssignmentCardV2 = ({
  id,
  name,
  due_date,
  course,
  repo_url,
}) => {
  const history = useHistory();
  const classes = useStyles();
  const due_days = Math.round((new Date(due_date) - new Date())/(1000*3600*24));
  return (

    <Box className={classes.asignmentContainer}>
      {due_days > 0 &&
        <Box
          className={
            clsx(classes.dueBadge,
              due_days > 7 ? classes.greenBadge :due_days <= 5 && due_days > 3 ? classes.orangeBadge : classes.redBadge)
          }
        >
          <Typography className={classes.dueDate} align='center'>
            {`${due_days} ${due_days == 1 ? 'day' : 'days'}`} remaining
          </Typography>
        </Box>
      }
      <Typography className={classes.assignmentName}>{name}</Typography>
      <Typography className={classes.courseName}>{course.name}</Typography>
      <Box className={classes.courseActionsContainer}>
        <Button
          onClick = {() => {
            history.push(`/courses/assignment?assignmentId=${id}`);
          }}
          className={classes.openCourseButton}
        >
            Open Assignment
        </Button>
        <Button
          onClick = {() => {
            history.push(repo_url);
          }}
          className={classes.viewRepoButon}
        >
          View Repo
        </Button>
      </Box>

    </Box>

  );
};


export default AssignmentCardV2;
