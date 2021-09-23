import React, {useState} from 'react';
import useSWR from 'swr';

import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import ProfileCard from '../../Components/Public/Profile/ProfileCard';
import StandardLayout from '../../Components/Layouts/StandardLayout';


const Profile = () => {
  const [_github_username, set_github_username] = useState(null);
  const {isValidating: loading, error, data} = useSWR('/api/public/auth/whoami');


  if (loading) return <CircularProgress/>;
  if (error) {
    window.location = '/api/public/auth/login';
    return null;
  }

  const user = data?.data?.user ?? null;
  const github_username = _github_username || user?.github_username;

  if (!user) {
    window.location = '/api/public/auth/login';
    return null;
  }

  return (
    <StandardLayout description={'Profile'}>
      <Grid container spacing={4} justify={'center'}>
        <Grid item xs={12} sm={10} md={8} lg={4}>
          <ProfileCard
            user={user}
            github_username={github_username}
            set_github_username={set_github_username}
          />
        </Grid>
      </Grid>
    </StandardLayout>
  );
};

export default Profile;


