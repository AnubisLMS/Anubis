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

import CourseItem from '../../../Components/Public/CourseItem/CourseItem';
import AssignmentItem from '../../../Components/Public/AssignmentItem/AssignmentItem';

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
      if (!data) return;
      const past = data?.assignments.filter((assignment) => {
        const assignmentDueDate = new Date(assignment.due_date);
        if (assignmentDueDate < new Date()) return assignment;
      });
      const active = data?.assignments.filter((assignment) => {
        const assignmentDueDate = new Date(assignment.due_date);
        if (assignmentDueDate >= new Date()) return assignment;
      });
      setActiveAssignments(active);
      console.log(active);
      setPastAssignments(past);
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
      {courses.map((course, index) => (
        <CourseItem
          key={index}
          name={course.name}
          instructor={course.professor_display_name}
          assignments={course.total_assignments}
          section={course.section}
          id={course.id}
        />
      ))}
      {console.log(activeAssignments)}
      {activeAssignments.map((assignment, index) => (
        <AssignmentItem
          key={index}
          name={assignment.name}
          course={assignment.course}
          repoUrl={assignment.repo_url}
          id={assignment.id}
          submitted={assignment.has_submission}
          dueDate={assignment.due_date}
        />
      ))}
      <SectionContainer title={'Courses'} link={'/courses'} linkTitle={'View All Courses'}>
        <Grid container spacing={6} className={classes.container}>
          {courses.length > 0 && courses ? courses.map((course, pos) => (
            <Grid item key={course.courseCode}>
              <CourseCard {... course}/>
            </Grid>
          )): (
            <Box className={classes.emptyContainer}>
              <Typography variant="h4" className={classes.emptyText}>You Have no Active Courses</Typography>
            </Box>
          )}
        </Grid>
      </SectionContainer>
      <SectionContainer title={'Active Assignments'}>
        <Grid container spacing={6} className={classes.container}>
          {activeAssignments.length > 0 && activeAssignments ? activeAssignments.map((assignment, index) => (
            <Grid item key={`${assignment.name}-${index}`}>
              <AssignmentCardV2 {... assignment} />
            </Grid>
          )) : (
            <Box className={classes.emptyContainer}>
              <Typography variant="h4" className={classes.emptyText}>You have no Active Assignments</Typography>
            </Box>
          )}
        </Grid>
      </SectionContainer>
      <SectionContainer title={'Past Assignments'}>
        <Grid container spacing={6} className={classes.container}>
          {pastAssignments.length > 0 && pastAssignments ? pastAssignments.map((assignment, index) => (
            <Grid item key={`${assignment.name}-${index}`}>
              <AssignmentCardV2 {... assignment} />
            </Grid>
          )): (
            <Box className={classes.emptyContainer}>
              <Typography variant="h4" className={classes.emptyText}>You have no Past Assignments</Typography>
            </Box>
          )}
        </Grid>
      </SectionContainer>
    </StandardLayout>
  );
};

export default Dashboard;
