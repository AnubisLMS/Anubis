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

import StandardLayout from '../../../Components/Shared/Layouts/StandardLayout';
import SectionHeader from '../../../Components/Shared/SectionHeader/SectionHeader.jsx';
import Divider from '../../../Components/Shared/Divider/Divider';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import {useStyles} from './Profile.styles';

const Profile = () => {
  const [_github_username, set_github_username] = useState(null);
  const {isValidating: loading, error, data} = useSWR('/api/public/auth/whoami');

  const [editToggled, setEditToggled] = useState(false);

  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  const user = data?.data?.user ?? null;
  const userGroup = user?.is_superuser ? 'Super User' : user?.is_admin ? 'Admin' : 'Student';
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
              <span className={userGroup === 'Super User' ?
                clsx(classes.userGroup, classes.super): userGroup === 'Admin' ?
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
          {editToggled ? (
            <TextField
              label="Github Username"
              onChange={(e) => set_github_username(e.target.value)}
              value={github_username}
              variant="outlined"
            />
          ): (
            <Typography className={classes.githubText}>
              {github_username}
            </Typography>
          )}
          {editToggled ? (
            <Button
              className={classes.saveButton}
              onClick={() => {
                handleSave();
                setEditToggled(false);
              }}
            >
              Save
            </Button>
          ): (
            <Button
              className={classes.editButton}
              onClick={() => setEditToggled(true)}
            >
              Edit
            </Button>
          )}
        </Box>
      </Box>
    </StandardLayout>
  );
};

export default Profile;


