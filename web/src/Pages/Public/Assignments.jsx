import React from 'react';

import {Redirect} from 'react-router-dom';

import Grid from '@material-ui/core/Grid';
import Grow from '@material-ui/core/Grow';
import CircularProgress from '@material-ui/core/CircularProgress';

import useGet from '../../hooks/useGet';
import useQuery from '../../hooks/useQuery';

import AssignmentCard from '../../Components/Public/Assignments/AssignmentCard';


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
    <Grid container>
      <Grid item xs={12}>
        <Grid container justify="left" spacing={4}>
          {data.assignments.map(translateAssignmentData).map((assignment, pos) => (
            <Grow
              key={assignment.assignmentId}
              in={true}
              style={{transformOrigin: '0 0 0'}}
              {...({timeout: 300 * (pos + 1)})}
            >
              <Grid item>
                <AssignmentCard assignment={assignment}/>
              </Grid>
            </Grow>
          ))}

        </Grid>
      </Grid>
    </Grid>
  );
}
