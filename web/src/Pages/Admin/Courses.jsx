import React, {useState} from 'react';

import Grid from '@material-ui/core/Grid';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import standardStatusHandler from '../../Utils/standardStatusHandler';

import makeStyles from '@material-ui/core/styles/makeStyles';

import {format} from 'date-fns';
import Typography from '@material-ui/core/Typography';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import CourseCard from '../../Components/Admin/Course/CourseCard';
import AuthContext from '../../Contexts/AuthContext';
import Button from '@material-ui/core/Button';


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
  const [professorCourses, setProfessorCourses] = useState([]);
  const [taCourses, setTaCourses] = useState([]);
  const [edits, setEdits] = useState(0);
  const [reset, setReset] = useState(0);

  React.useEffect(() => {
    axios.get('/api/admin/courses/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.ta_courses) {
        setTaCourses(data.ta_courses);
      }
      if (data?.professor_courses) {
        setProfessorCourses(data.professor_courses);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  const updateField = (id, field, toggle = false, datetime = false) => (e) => {
    if (!e) {
      return;
    }

    for (const course of professorCourses) {
      if (course.id === id) {
        if (toggle) {
          course[field] = !course[field];
          break;
        }

        if (datetime) {
          course[field] = format(e, 'yyyy-MM-dd HH:mm:ss');
          break;
        }

        course[field] = e.target.value.toString();
        break;
      }
    }
    setProfessorCourses(professorCourses);
    setEdits((state) => ++state);
  };

  const saveCourse = (id) => () => {
    for (const course of professorCourses) {
      if (course.id === id) {
        axios.post(`/api/admin/courses/save`, {course}).then((response) => {
          standardStatusHandler(response, enqueueSnackbar);
        }).catch(standardErrorHandler(enqueueSnackbar));
      }
    }
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
      <Grid item/>
      <Grid item xs={12} md={10}>
        <Grid container spacing={4}>
          {professorCourses.map((course) => (
            <Grid item xs={12} md={6} lg={4} key={course.id}>
              <CourseCard
                course={course}
                editableFields={editableFields}
                updateField={updateField}
                saveCourse={saveCourse}
                _disabled={false}
              />
            </Grid>
          ))}
          {taCourses.map((course) => (
            <Grid item xs={12} md={6} lg={4} key={course.id}>
              <CourseCard
                course={course}
                editableFields={editableFields}
                updateField={updateField}
                saveCourse={saveCourse}
                _disabled={true}
              />
            </Grid>
          ))}
        </Grid>
      </Grid>
    </Grid>
  );
}
