import React, {useState} from 'react';
import axios from 'axios';
import {format} from 'date-fns';
import {useSnackbar} from 'notistack';
import {Route, Switch} from 'react-router-dom';

import Grid from '@material-ui/core/Grid';

import Button from '@material-ui/core/Button';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Typography from '@material-ui/core/Typography';

import {PageTitle} from '../../Components/Shared';
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
  {field: 'autograde_tests_repo', label: 'Autograde Tests Repo'},
  {field: 'theia_default_image', label: 'Theia Default Image'},
  {field: 'theia_default_options', label: 'Theia Default Options'},
  {field: 'github_org_url', label: 'Github Org URL'},
  {field: 'join_code', label: 'Join Code'},
];

export default function Course() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [course, setCourse] = useState(null);
  const [edits, setEdits] = useState(0);
  const [reset, setReset] = useState(0);

  React.useEffect(() => {
    axios.get('/api/admin/courses/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.course) {
        data.course.theia_default_options = JSON.stringify(data.course.theia_default_options);
        setCourse(data.course);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  const updateField = (id, field, toggle = false, datetime = false, json = false) => (e) => {
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
    const post_course = {...course};
    try {
      post_course.theia_default_options = JSON.parse(course.theia_default_options);
    } catch (e) {
      enqueueSnackbar(e.toString(), {variant: 'error'});
      return;
    }
    axios.post(`/api/admin/courses/save`, {course: post_course}).then((response) => {
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

  if (!course) {
    return null;
  }

  return (
    <Grid container spacing={4} justify={'center'} alignItems={'center'}>
      <PageTitle {... {description: 'Course Management'}} />
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

      <Switch>
        <Route path={'/admin/course'} exact={true}>
          <Grid item xs={12} sm={10} md={8}>
            <CourseCard
              course={course}
              editableFields={editableFields}
              updateField={updateField}
              saveCourse={saveCourse}
              _disabled={false}
            />
          </Grid>
        </Route>
        <Route path={'/admin/course/tas'} exact={false}>
          <Grid item xs={12} sm={10} md={8}>
            <CourseTasProfessors base={'ta'}/>
          </Grid>
        </Route>
        <Route path={'/admin/course/professors'}>
          <Grid item xs={12} sm={10} md={8}>
            <CourseTasProfessors base={'professor'}/>
          </Grid>
        </Route>
      </Switch>

    </Grid>
  );
}
