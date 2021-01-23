import React, {useState} from 'react';

import {Redirect} from 'react-router-dom';

import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import useGet from '../../hooks/useGet';

import ProfileCard from '../../Components/Public/Profile/ProfileCard';
import Typography from '@material-ui/core/Typography';


export default function Profile() {
  const [_github_username, set_github_username] = useState(null);
  const [{loading, error, data}] = useGet('/api/public/auth/whoami');

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  const {user} = data;

  const github_username = _github_username || user.github_username;

  return (
    <Grid container spacing={4} alignItems="center">
      <Grid item>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Profile
        </Typography>
      </Grid>

      <Grid item xs={12}>
        <Grid container spacing={4} justify={'center'}>
          <Grid item xs={12} sm={10} md={8} lg={4}>
            <ProfileCard
              user={user}
              github_username={github_username}
              set_github_username={set_github_username}
            />
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
}

