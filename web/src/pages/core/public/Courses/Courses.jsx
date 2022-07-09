import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import TextField from '@mui/material/TextField';

import {useStyles} from './Courses.styles';
import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import standardErrorHandler from '../../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import SectionHeader from '../../../../components/shared/SectionHeader/SectionHeader';
import JoinCourseItem from '../../../../components/core/JoinCourseItem/JoinCourseItem';
import CourseItem from '../../../../components/core/CourseItem/CourseItem';
import Divider from '../../../../components/shared/Divider/Divider';
import ListHeader from '../../../../components/shared/ListHeader/ListHeader';

const joinCourse = (state, enqueueSnackbar) => () => {
  const {joinCode, setReset} = state;
  axios.get(`/api/public/courses/join/${encodeURIComponent(joinCode)}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
      if (data.status.match(/Joined/)) {
        setReset((prev) => ++prev);
      }
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};


const Courses = () => {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [courses, setCourses] = useState([]);
  const [joinCode, setJoinCode] = useState(null);
  const [joinOpen, setJoinOpen] = useState(false);
  const [reset, setReset] = useState(0);

  React.useEffect(() => {
    axios.get('/api/public/courses/').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setCourses(data.courses);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  const state = {
    courses, setCourses,
    joinCode, setJoinCode,
    joinOpen, setJoinOpen,
    reset, setReset,
  };

  return (
    <StandardLayout>
      <Dialog
        open={joinOpen}
        onClose={() => setJoinOpen(false)}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">Join an Anubis Class</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Provide your join code here to join your class!
          </DialogContentText>
          <TextField
            placeholder={'Join Code'}
            variant={'outlined'}
            style={{width: '100%'}}
            value={joinCode}
            onChange={(e) => setJoinCode(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button
            color="primary"
            variant={'contained'}
            onClick={joinCourse(state, enqueueSnackbar)}
            autoFocus
          >
            Join
          </Button>
        </DialogActions>
      </Dialog>
      <SectionHeader title={'Courses'} isPage/>
      <Divider/>
      <ListHeader sections={['Course Name', 'Professor', 'Number of Assignments', 'Actions']}/>
      {courses && courses.map((course, index) => (
        <CourseItem
          key={`${course.name}-${index}`}
          name={course.name}
          section={course.section}
          instructor={course.professor_display_name}
          assignments={course.total_assignments}
          id={course.id}
        />
      ))}
      <JoinCourseItem callback={() => setJoinOpen(true)}/>
    </StandardLayout>
  );
};

export default Courses;

