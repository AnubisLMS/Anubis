import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import Box from '@material-ui/core/Box';

import StandardLayout from '../../../Components/Shared/Layouts/StandardLayout';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import {useStyles} from './Dashboard.styles';
import useQuery from '../../../Hooks/useQuery';

import CourseItem from '../../../Components/Public/CourseItem/CourseItem';
import AssignmentItem from '../../../Components/Public/AssignmentItem/AssignmentItem';
import SectionHeader from '../../../Components/Shared/SectionHeader/SectionHeader';

const Dashboard = () => {
  const query = useQuery();
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [courses, setCourses] = useState([]);
  const [activeAssignments, setActiveAssignments] = useState([]);

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
      const active = data?.assignments.filter((assignment) => {
        const assignmentDueDate = new Date(assignment.due_date);
        if (assignmentDueDate >= new Date()) return assignment;
      });
      setActiveAssignments(active);
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  return (
    <StandardLayout>
      <SectionHeader isPage title='Anubis LMS Dashboard' />
      <Box className={classes.divider} />
      <SectionHeader
        title='Courses'
        linkText='View All Courses'
        link='/courses'
      />
      {courses.map((course, index) => (
        <CourseItem
          key={`${course.name}-${index}`}
          name={course.name}
          instructor={course.professor_display_name}
          assignments={course.total_assignments}
          section={course.section}
          id={course.id}
        />
      ))}
      {activeAssignments && (
        <SectionHeader
          title='Active Assignments'
          linkText='View All Assignments'
          link='/courses/assignments'
        />
      )}
      {activeAssignments && activeAssignments.map((assignment, index) => (
        <AssignmentItem
          key={`${assignment.name}-${index}`}
          name={assignment.name}
          course={assignment.course}
          repoUrl={assignment.repo_url}
          id={assignment.id}
          submitted={assignment.has_submission}
          dueDate={assignment.due_date}
        />
      ))}
    </StandardLayout>
  );
};

export default Dashboard;
