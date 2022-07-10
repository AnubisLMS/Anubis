import React, {useState, useEffect} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import SchoolIcon from '@mui/icons-material/School';
import Divider from '@mui/material/Divider';

import standardStatusHandler from '../../../../utils/standardStatusHandler';
import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import {useStyles} from './Course.styles';
import useQuery from '../../../../hooks/useQuery';
import standardErrorHandler from '../../../../utils/standardErrorHandler';
import AssignmentItem from '../../../../components/core/AssignmentItem/AssignmentItem';


const Course = () => {
  const query = useQuery();
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  const [course, setCourse] = useState(null);
  const [assignments, setAssignments] = useState(null);

  const courseId = query.get('courseId');

  React.useEffect(() => {
    axios.get(`/api/public/courses/get/${courseId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setCourse(data.course);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);


  React.useEffect(() => {
    axios.get('/api/public/assignments', {params: {courseId: courseId}}).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setAssignments(data.assignments);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);


  return (
    <StandardLayout>
      {course && (
        <Box className={classes.root}>
          <Box position="sticky" top={42} className={classes.header}>
            <Box className={classes.headerLeft}>
              <Box className={classes.iconOuterCircle}>
                <Box className={classes.iconInnerCircle}>
                  <SchoolIcon />
                </Box>
              </Box>
              <Box className={classes.headerText}>
                <Typography className={classes.headerAssignmentName}>
                  {course.name}
                </Typography>
                <Typography className={classes.headerCourseName}>
                  Section {course.section}
                </Typography>
              </Box>
            </Box>
          </Box>
          <Divider />
          <Box className = {classes.content}>
            <Typography className={classes.sectionHeader}>
              Instructors / Teaching Assistants
            </Typography>
            <Box className={classes.overviewItem}>
              {course?.tas && course.tas.map((ta, index) => (
                <Typography key={`${ta.name}-${index}`} className={classes.overviewItemSubtitle}>
                  <p><span className={classes.op}>Name: </span> {ta.name}</p>
                  <p><span className={classes.op}>Email: </span> {`${ta.netid}@nyu.edu`}</p>
                </Typography>
              ))}
            </Box>
            <br />
            <br />
            <Typography className={classes.sectionHeader}>
              Assignments
            </Typography>
            {assignments && assignments.map((assignment, index) => (
              <AssignmentItem
                key={`${assignment.name}-${index}`}
                name={assignment.name}
                dueDate={assignment.due_date}
                id={assignment.id}
                course={assignment.course}
                submitted={assignment.has_submission}
                visible_to_students={assignment.visible_to_students}
              />
            ))}
          </Box>
        </Box>
      )}
    </StandardLayout>
  );
};

export default Course;
