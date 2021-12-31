import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import TextField from '@material-ui/core/TextField';
import Box from '@material-ui/core/Box';

import {useStyles} from './Courses.styles';
import StandardLayout from '../../../Components/Shared/Layouts/StandardLayout';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import SectionHeader from '../../../Components/Shared/SectionHeader/SectionHeader';
import JoinCourseItem from '../../../Components/Public/JoinCourseItem/JoinCourseItem';
import CourseItem from '../../../Components/Public/CourseItem/CourseItem';
import Divider from '../../../Components/Shared/Divider/Divider';
import ListHeader from '../../../Components/Shared/ListHeader/ListHeader';

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
      <SectionHeader title={'Courses'} isPage />
      <Divider />
      <ListHeader sections={['Course Name', 'Professor', 'Number of Assignments', 'Actions']} />
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
      <JoinCourseItem callback={() => setJoinOpen(true)} />
    </StandardLayout>
  );
};

export default Courses;

