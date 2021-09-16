import React from 'react';
import {useHistory} from 'react-router-dom';

import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';

import {useStyles} from './CourseCard.styles';

const CourseCardV2 = ({
  id,
  name,
  professor_display_name,
  total_assignments,
}) => {
  const classes = useStyles();
  const history = useHistory();

  return (
    <Box className={classes.courseCardContainer}>
      <Typography className={classes.courseName}>{name}</Typography>
      <Typography className={classes.instructorName}>Instructor: {professor_display_name}</Typography>
      <Box className={classes.courseActionsContainer}>
        <Button
          onClick = {() => {
            history.push(`/courses/assignments?courseId=${id}`);
          }}
          className={classes.openCourseButton}
        >
          Open Course
        </Button>
        <Typography className={classes.totalAssignments}>{total_assignments} Assignments</Typography>
      </Box>
    </Box>
  );
};

export default CourseCardV2;

