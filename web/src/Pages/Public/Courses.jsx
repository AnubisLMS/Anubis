import React from 'react';

import {Redirect} from 'react-router-dom';

import Grid from '@material-ui/core/Grid';
import Grow from '@material-ui/core/Grow';
import CircularProgress from '@material-ui/core/CircularProgress';

import useGet from '../../hooks/useGet';

import CourseCard from '../../Components/Public/Courses/CourseCard';
import Typography from '@material-ui/core/Typography';

export default function CourseView() {
  // const{courses} = props; maps to the request for current student courses.
  const [{loading, error, data}] = useGet('/api/public/courses/');

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  return (
    <Grid container spacing={4} justify={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Courses
        </Typography>
      </Grid>
      <Grid item/>
      <Grid item xs={12} md={10}>
        <Grid container spacing={4}>
          {data.classes.map((course, pos) => (
            <Grid item xs key={course.courseCode}>
              <Grow
                key={course.courseCode}
                in={true}
                style={{transformOrigin: '0 0 0'}}
                {...({timeout: 300 * (pos + 1)})}
              >
                <CourseCard course={course}/>
              </Grow>
            </Grid>
          ))}
        </Grid>
      </Grid>
    </Grid>
  );
}
