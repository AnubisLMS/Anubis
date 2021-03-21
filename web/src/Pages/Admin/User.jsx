import React, {useState} from 'react';

import Grid from '@material-ui/core/Grid';

import useQuery from '../../hooks/useQuery';
import UserCard from '../../Components/Admin/Users/UserCard';
import CourseCard from '../../Components/Admin/Users/CourseCard';
import axios from 'axios';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import {useSnackbar} from 'notistack';
import Typography from '@material-ui/core/Typography';


export default function User() {
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [user, setUser] = useState(null);
  const [edits, setEdits] = useState(0);

  React.useEffect(() => {
    axios.get(`/api/admin/students/info/${query.get('userId')}`).then((response) => {
      if (standardStatusHandler(response, enqueueSnackbar)) {
        setUser(response?.data?.data);
      }
    });
  }, [edits]);

  if (!user) {
    return null;
  }

  const pageState = {
    user, setUser,
    edits, setEdits,
  };

  return (
    <Grid container spacing={4} justify={'center'} alignItems={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Student Management
        </Typography>
      </Grid>
      <Grid item xs={12} md={4} key={'user-card'}>
        <UserCard user={user} setUser={setUser}/>
      </Grid>
      <Grid item xs={12} md={4}>
        <Grid container spacing={2} justify={'center'} alignItems={'flex-start'}>
          {user.courses.map((course) => (
            <Grid item xs key={'course-card'}>
              <CourseCard student={user.student} course={course}/>
            </Grid>
          ))}
        </Grid>
      </Grid>
    </Grid>
  );
}
