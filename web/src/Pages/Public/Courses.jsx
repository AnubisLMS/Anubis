import React from 'react';

import {Redirect} from 'react-router-dom';

import Grid from '@material-ui/core/Grid';
import Grow from '@material-ui/core/Grow';
import CircularProgress from '@material-ui/core/CircularProgress';

import useGet from '../../hooks/useGet';

import CourseCard from '../../Components/Public/Courses/CourseCard';

export default function CourseView() {
  // const{courses} = props; maps to the request for current student courses.
  const [{loading, error, data}] = useGet('/api/public/courses/');

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  return (
    <Grid container>
      <Grid item xs={12}>
        <Grid container justify="left" spacing={4}>
          {data.classes.map((course, pos) => (
            <Grow
              key={course.courseCode}
              in={true}
              style={{transformOrigin: '0 0 0'}}
              {...({timeout: 300 * (pos + 1)})}
            >
              <Grid item>
                <CourseCard course={course}/>
              </Grid>
            </Grow>
          ))}
        </Grid>

      </Grid>
    </Grid>
  );
}
