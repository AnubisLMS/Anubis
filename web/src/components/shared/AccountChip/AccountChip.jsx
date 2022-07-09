import React, {useState} from 'react';
import {useHistory} from 'react-router-dom';

import {useStyles} from './AccountChip.styles';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const AccountChip = ({user, netid, onContextChange, course}) => {
  const classes = useStyles();
  const history = useHistory();

  const [open, setOpen] = useState(false);

  return (
    <Box className={classes.root}>
      <Typography className={classes.netid}>
        {netid}
      </Typography>
      <Box className={classes.clickableContainer} onClick={() => setOpen(!open)}>
        <Box className={classes.avatar}>
          {netid.substring(0, 1).toUpperCase()}
        </Box>
        <Box className={classes.expandIcon}>
          {open ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </Box>
      </Box>
      {open &&
        <Box className={classes.profileActions}>
          {user?.is_admin && user?.ta_for && user?.ta_for.length > 0 &&
            <Box>
              <Typography className={classes.contextTitle}> CONTEXT </Typography>
              {user.ta_for.map((selectedCourse, index) => (
                <Box
                  key={`${selectedCourse.name}-${index}`}
                  className={course.id === selectedCourse.id ? classes.selectedCourse : classes.course}
                  onClick={() => onContextChange(selectedCourse)}
                >
                  <Typography className={classes.courseName}>{selectedCourse.name}</Typography>
                </Box>
              ))}
              <Divider />
            </Box>
          }
          <Box
            mt='10px'
            onClick={() => {
              history.push('/profile');
              setOpen(false);
            }}
            className={classes.profileAction}
          >
            <Typography className={classes.profileActionText}>
              View Profile
            </Typography>
          </Box>
          <Box className={classes.profileAction} component={'a'} href={'/api/public/auth/login'}>
            <Typography className={classes.profileActionText}>
              Log In
            </Typography>
          </Box>
          <Box className={classes.profileAction} component={'a'} href={'/api/public/auth/logout'}>
            <Typography className={classes.profileActionText}>
              Log Out
            </Typography>
          </Box>
        </Box>
      }
    </Box>
  );
};

export default AccountChip;
