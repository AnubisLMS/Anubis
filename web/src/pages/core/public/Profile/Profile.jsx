import React, {useState, useEffect} from 'react';
import useSWR from 'swr';
import axios from 'axios';
import clsx from 'clsx';
import {useSnackbar} from 'notistack';

import CircularProgress from '@material-ui/core/CircularProgress';
import TextField from '@material-ui/core/TextField';
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';

import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import SectionHeader from '../../../../components/shared/SectionHeader/SectionHeader.jsx';
import Divider from '../../../../components/shared/Divider/Divider';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';
import {useStyles} from './Profile.styles';
import {GitHub} from '@material-ui/icons';

const Profile = () => {
  const [_github_username, set_github_username] = useState(null);
  const {isValidating: loading, error, data} = useSWR('/api/public/auth/whoami');

  const [editToggled, setEditToggled] = useState(false);

  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  const user = data?.data?.user ?? null;
  const userGroup = user?.is_superuser ? 'super User' : user?.is_admin ? 'admin' : 'Student';
  const github_username = _github_username || user?.github_username;

  const handleSave = () => {
    axios.post(`/api/public/auth/set-github-username`, {github_username}).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  if (loading) return <CircularProgress/>;
  if (error) {
    window.location = '/api/public/auth/login';
    return null;
  }

  if (!user) {
    window.location = '/api/public/auth/login';
    return null;
  }

  return (
    <StandardLayout>
      <Box className={classes.bioContainer}>
        <Box className={classes.rowFlex}>
          <Box className={classes.profilePic}>
            <Typography className={classes.letter}> {user.name[0]}</Typography>
          </Box>
          <Box className={classes.profileText}>
            <Typography className={classes.name}>
              {user.name.trim()}
            </Typography>
            <Typography className={classes.netid}>
              {user.netid.trim()}
            </Typography>
          </Box>
        </Box>
        <Box className={classes.rowFlex}>
          <Box className={classes.userTypes}>
            <Typography>
              User Group:
              <span className={userGroup === 'super User' ?
                clsx(classes.userGroup, classes.super): userGroup === 'admin' ?
                  clsx(classes.userGroup, classes.admin): classes.userGroup}
              >
                {userGroup}
              </span>
            </Typography>
          </Box>
        </Box>
      </Box>

      <SectionHeader title={'Profile'} />
      <Divider />
      <Box className={classes.fieldsContainer}>
        <Box className={classes.githubContainer}>
          <Typography className={classes.githubText}>
            Github Username
          </Typography>
          <Typography className={classes.githubText}>
            {github_username ?? 'Not Set'}
          </Typography>
          <Button
            startIcon={<GitHub/>}
            className={classes.saveButton}
            component="a"
            href="/api/public/github/login"
          >
            Link Account with Github
          </Button>
        </Box>
      </Box>
    </StandardLayout>
  );
};

export default Profile;


