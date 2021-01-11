import React, {useState} from 'react';

import {Redirect} from 'react-router-dom';

import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import useQuery from '../../hooks/useQuery';
import useGet from '../../hooks/useGet';
import UserCard from '../../Components/Admin/Users/UserCard';
import CourseCard from '../../Components/Admin/Users/CourseCard';


export default function User() {
  const [{loading, error, data}] = useGet(`/api/admin/students/info/${useQuery().get('userId')}`);
  const [user, setUser] = useState(null);

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  if (user === null) {
    setUser(data);
    return null;
  }

  return (
    <Grid container spacing={2} justify={'center'} alignItems={'center'} direction={'column'}>
      <Grid item xs key={'user-card'}>
        <UserCard user={user} setUser={setUser}/>
      </Grid>
      {user.courses.map((course) => (
        <Grid item xs key={'course-card'}>
          <CourseCard student={user.student} course={course}/>
        </Grid>
      ))}
    </Grid>
  );
}
