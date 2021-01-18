import React from 'react';

import {Redirect} from 'react-router-dom';

import Grid from '@material-ui/core/Grid';
import Grow from '@material-ui/core/Grow';
import CircularProgress from '@material-ui/core/CircularProgress';

import useGet from '../../hooks/useGet';
import useQuery from '../../hooks/useQuery';

import AssignmentCard from '../../Components/Public/Assignments/AssignmentCard';
import Typography from '@material-ui/core/Typography';


export default function AssignmentView() {
  const query = useQuery();
  const [{loading, error, data}] = useGet(
    '/api/public/assignments/',
    query.course ? {course: query.course} : {});

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  const translateAssignmentData = ({
    id,
    name,
    due_date,
    course,
    description,
    has_submission,
    github_classroom_link,
  }, index) => ({
    courseCode: course.class_code, assignmentId: id, assignmentTitle: name, dueDate: due_date,
    hasSubmission: has_submission, assignmentDescription: description,
    assignmentNumber: data.assignments.length - index, githubClassroomLink: github_classroom_link,
  });

  return (
    <Grid container spacing={4}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Assignments
        </Typography>
      </Grid>
      {data.assignments.map(translateAssignmentData).map((assignment, pos) => (
        <Grid item xs={12} md={3} key={assignment.assignmentId}>
          <Grow
            in={true}
            style={{transformOrigin: '0 0 0'}}
            {...({timeout: 300 * (pos + 1)})}
          >
            <AssignmentCard assignment={assignment}/>
          </Grow>
        </Grid>
      ))}
    </Grid>
  );
}
