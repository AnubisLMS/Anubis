import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import {Link} from 'react-router-dom';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import Grid from '@material-ui/core/Grid';
import Grow from '@material-ui/core/Grow';

import AssignmentCardV2 from '../../../Components/Public/Assignments/AssignmentCardV2/AssignmentCardV2';
import CourseCard from '../../../Components/Public/Courses/CourseCard/CourseCard';
import StandardLayout from '../../../Components/Layouts/StandardLayout';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import {useStyles} from './Dashboard.styles';
import useQuery from '../../../hooks/useQuery';

const Dashboard = () => {
  const query = useQuery();
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [courses, setCourses] = useState([]);
  const [activeAssignments, setActiveAssignments] = useState([]);
  const [pastAssignments, setPastAssignments] = useState([]);

  useEffect(() => {
    axios.get('/api/public/courses/').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setCourses(data.courses);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  useEffect(() => {
    axios.get('/api/public/assignments', {params: {courseId: query.get('courseId')}}).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        data.assignments.map((assignment) => {
          const assignmentDueDate = new Date(assignment.dueDate);
          if (assignmentDueDate < new Date()) {
            setPastAssignments(pastAssignments.concat(assignment));
          } else {
            setActiveAssignments(activeAssignments.concat(assignment));
          }
        });
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  const SectionContainer = ({children, title, link, linkTitle}) => (
    <Box className={classes.sectionContainer}>
      <Box className={classes.sectionHeader}>
        <Typography className={classes.sectionHeaderTitle}>
          {title}
        </Typography>
        <Link to={link} className={classes.sectionHeaderLink}>
          {linkTitle}
        </Link>
      </Box>
      <Box className={classes.sectionChildContainer}>
        {children}
      </Box>
    </Box>
  );

  return (
    <StandardLayout>
      <SectionContainer title={'Courses'} link={'/courses'} linkTitle={'View All Courses'}>
        <Grid container spacing={4}>
          {courses.map((course, pos) => (
            <Grid item key={course.courseCode}>
              <Grow
                in={true}
                style={{transformOrigin: '0 0 0'}}
                timeout={300 * (pos + 1)}
              >
                <CourseCard {... course}/>
              </Grow>
            </Grid>
          ))}
        </Grid>
      </SectionContainer>
      <SectionContainer title={'Active Assignments'}>
      </SectionContainer>
      <SectionContainer title={'Past Assignments'}>
        {pastAssignments.map((assignment, index) => (
          <Grid item key={assignment.name}>
            <h1>Hello</h1>
            <Grow
              in={true}
              style={{transformOrigin: '0 0 0'}}
              timeout={300 * (index + 1)}
            >
              <AssignmentCardV2 {... assignment}/>
            </Grow>
          </Grid>
        ))}
      </SectionContainer>
    </StandardLayout>
  );
};

export default Dashboard;
