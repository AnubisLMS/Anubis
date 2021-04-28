import React, {useState} from 'react';
import axios from 'axios';
import {format} from 'date-fns';
import {useSnackbar} from 'notistack';
import {Route, Switch} from 'react-router-dom';

import Grid from '@material-ui/core/Grid';

import Button from '@material-ui/core/Button';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Typography from '@material-ui/core/Typography';

import CourseCard from '../../Components/Admin/Course/CourseCard';
import AuthContext from '../../Contexts/AuthContext';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import CourseTasProfessors from '../../Components/Admin/Course/CourseTasProfessors';


const useStyles = makeStyles((theme) => ({
  root: {
    minWidth: 275,
  },
  title: {
    fontSize: 14,
  },
  pos: {
    marginBottom: 12,
  },
  button: {
    margin: theme.spacing(1),
  },
}));

const editableFields = [
  {field: 'name', label: 'Course Name'},
  {field: 'course_code', label: 'Course Code'},
  {field: 'section', label: 'Section'},
  {field: 'professor', label: 'Professor'},
  {field: 'join_code', label: 'Join Code', disabled: true},
];

export default function Courses() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [course, setCourse] = useState([]);
  const [edits, setEdits] = useState(0);
  const [reset, setReset] = useState(0);

  React.useEffect(() => {
    axios.get('/api/admin/courses/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.course) {
        setCourse(data.course);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  const updateField = (id, field, toggle = false, datetime = false) => (e) => {
    if (!e) {
      return;
    }

    if (course.id === id) {
      if (toggle) {
        course[field] = !course[field];
      } else if (datetime) {
        course[field] = format(e, 'yyyy-MM-dd HH:mm:ss');
      } else {
        course[field] = e.target.value.toString();
      }
    }
    setCourse(course);
    setEdits((state) => ++state);
  };

  const saveCourse = () => () => {
    axios.post(`/api/admin/courses/save`, {course}).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const createCourse = () => {
    axios.get('/api/admin/courses/new').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setReset((prev) => ++prev);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };


  return (
    <Grid container spacing={4} justify={'center'} alignItems={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Course Management
        </Typography>
      </Grid>
      <Switch>
        <Route path={'/admin/courses'} exact>
          <AuthContext.Consumer>
            {(user) => (
              <>
                {!!user ? (
                  <Grid item xs={12}>
                    <Button
                      variant={'contained'}
                      color={'primary'}
                      onClick={createCourse}
                    >
                  Create Course
                    </Button>
                  </Grid>
                ) : null}
              </>
            )}
          </AuthContext.Consumer>
        </Route>
      </Switch>
      <Grid item/>
      <Grid item xs={12} md={10}>
        <Grid container spacing={4}>
          <Switch>
            <Route path={'/admin/courses'} exact={true}>
              <React.Fragment>
                <Grid item xs={12} md={6} key={course.id}>
                  <CourseCard
                    course={course}
                    editableFields={editableFields}
                    updateField={updateField}
                    saveCourse={saveCourse}
                    _disabled={false}
                  />
                </Grid>
              </React.Fragment>
            </Route>
            <Route path={'/admin/courses/tas'} exact={false}>
              <CourseTasProfessors base={'ta'}/>
            </Route>
            <Route path={'/admin/courses/professors'}>
              <CourseTasProfessors base={'professor'}/>
            </Route>
          </Switch>
        </Grid>
      </Grid>
    </Grid>
  );
}
