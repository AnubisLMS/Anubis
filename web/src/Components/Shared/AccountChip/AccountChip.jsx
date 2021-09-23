import React, {useState} from 'react';

import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import {useStyles} from './AccountChip.styles';

const AccountChip = ({user, netid, onContextChange, course}) => {
  const classes = useStyles();

  const [open, setOpen] = useState(false);
  console.log(user);
  console.log(course);

  return (
    <Box className={classes.root}>
      <Typography className={classes.netid}>
        {netid}
      </Typography>
      <Box onClick={() => setOpen(!open)} className={classes.avatar}>
        {netid.substring(0, 1).toUpperCase()}
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
          <Box mt='10px'className={classes.profileAction}>
            <Typography className={classes.profileActionText}>
              View Profile
            </Typography>
          </Box>
          <Box className={classes.profileAction}>
            <Typography className={classes.profileActionText}>
              Log In
            </Typography>
          </Box>
          <Box className={classes.profileAction}>
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
