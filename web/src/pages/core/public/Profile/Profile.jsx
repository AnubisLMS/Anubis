import React, {useState} from 'react';
import axios from 'axios';
import clsx from 'clsx';
import {useSnackbar} from 'notistack';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import GitHub from '@mui/icons-material/GitHub';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';

import {useStyles} from './Profile.styles';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';
import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import SectionHeader from '../../../../components/shared/SectionHeader/SectionHeader.jsx';
import Divider from '../../../../components/shared/Divider/Divider';
import DeletePvc from '../../../../components/core/Profile/DeletePvc';
import PrivacyPolicyModal from '../../../../components/shared/PrivacyPolicy/PrivacyPolicyModal';

const Profile = () => {
  const [user, setUser] = useState(null);
  const [userGroup, setUserGroup] = useState(null);
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  React.useEffect(() => {
    axios.get('/api/public/auth/whoami').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.user) {
        setUser(data.user);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  React.useEffect(() => {
    if (!user) return undefined;
    setUserGroup(user.is_superuser ? 'superuser' : user.is_admin ? 'admin' : 'student');
  }, [user]);

  const handleToggle = (key) => {
    axios.get(`/api/public/profile/toggle-email-notifications/${key}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.user) {
        setUser(data.user);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  if (!user) {
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
              <span className={userGroup === 'superuser' ?
                clsx(classes.userGroup, classes.super) : userGroup === 'admin' ?
                  clsx(classes.userGroup, classes.admin) : classes.userGroup}
              >
                {userGroup}
              </span>
            </Typography>
          </Box>
        </Box>
      </Box>

      <SectionHeader title={'Profile'}/>
      <Divider/>
      <Box className={classes.fieldsContainer}>
        <Box className={classes.githubContainer}>
          <Typography className={classes.githubText}>
            Github Username
          </Typography>
          <Typography className={classes.githubText}>
            {user?.github_username ?? 'Account Not Linked'}
          </Typography>
          <Button
            startIcon={<GitHub/>}
            className={classes.saveButton}
            variant={'contained'}
            component="a"
            href="/api/public/github/login"
          >
            Link Account with Github
          </Button>
        </Box>
      </Box>
      {[
        {key: 'deadline_email_enabled', title: 'Deadline Notifications'},
        {key: 'release_email_enabled', title: 'Release Notifications '},
      ].map((({key, title}) => (
        <Box className={classes.fieldsContainer} key={key}>
          <Box className={classes.githubContainer}>
            <Typography className={classes.githubText}>
              {title}
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={user[key]}
                  onChange={() => handleToggle(key)}
                  name={title}
                />
              }
            />
          </Box>
        </Box>
      )))}
      <Box className={classes.fieldsContainer}>
        <Box className={classes.githubContainer}>
          <Typography className={classes.githubText}>
            Delete my IDE Volume
          </Typography>
          <DeletePvc/>
        </Box>
      </Box>
      <Box className={classes.fieldsContainer}>
        <Box className={classes.githubContainer}>
          <Typography className={classes.githubText}>
            Privacy Policy
          </Typography>
          <PrivacyPolicyModal/>
        </Box>
      </Box>
    </StandardLayout>
  );
};

export default Profile;


