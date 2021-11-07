import React, {useState, useEffect} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import SchoolIcon from '@material-ui/icons/School';
import Divider from '@material-ui/core/Divider';

import standardStatusHandler from '../../../Utils/standardStatusHandler';
import StandardLayout from '../../../Components/Layouts/StandardLayout';
import {useStyles} from './Course.styles';
import useQuery from '../../../hooks/useQuery';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import AssignmentItem from '../../../Components/Public/AssignmentItem/AssignmentItem';


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
      console.log(data?.course);
      if (data) {
        setCourse(data.course);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);


  useEffect(() => {
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
              />
            ))}
          </Box>
        </Box>
      )}
    </StandardLayout>
  );
};

export default Course;
