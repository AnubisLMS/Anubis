import React, {useState} from 'react';

import Grid from '@material-ui/core/Grid';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import makeStyles from '@material-ui/core/styles/makeStyles';
import TextField from '@material-ui/core/TextField';
import DateFnsUtils from '@date-io/date-fns';
import {KeyboardDatePicker, KeyboardTimePicker, MuiPickersUtilsProvider} from '@material-ui/pickers';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';
import CardActionArea from '@material-ui/core/CardActionArea';
import Button from '@material-ui/core/Button';
import {format} from 'date-fns';
import Typography from '@material-ui/core/Typography';


const useStyles = makeStyles((theme) => ({
  root: {
    minWidth: 275,
  },
  bullet: {
    display: 'inline-block',
    margin: '0 2px',
    transform: 'scale(0.8)',
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

// const createCourse = (state, enqueueSnackbar) => () => {
//   const {setReset} = state;
//   axios.get('/api/admin/courses/new').then((response) => {
//     const data = standardStatusHandler(response, enqueueSnackbar);
//     if (data) {
//       setReset((prev) => ++prev);
//     }
//   }).catch(standardErrorHandler(enqueueSnackbar));
// };


export default function Courses() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [courses, setCourses] = useState([]);
  const [edits, setEdits] = useState(0);
  const [reset, setReset] = useState(0);

  React.useEffect(() => {
    axios.get('/api/admin/courses/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setCourses(data.courses);
      }
    }).catch((error) => enqueueSnackbar(error.toString(), {variant: 'error'}));
  }, [reset]);

  const updateField = (id, field, toggle = false, datetime = false) => (e) => {
    if (!e) {
      return;
    }

    for (const course of courses) {
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
    setCourses(courses);
    setEdits((state) => ++state);
  };

  const saveCourse = (id) => () => {
    for (const course of courses) {
      if (course.id === id) {
        axios.post(`/api/admin/courses/save`, {course}).then((response) => {
          standardStatusHandler(response, enqueueSnackbar);
        }).catch((error) => enqueueSnackbar(error.toString(), {variant: 'error'}));
        return;
      }
    }

    enqueueSnackbar('An error occurred', {variant: 'error'});
  };

  // const state = {
  //   courses, setCourses,
  //   edits, setEdits,
  //   reset, setReset,
  // };

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
      {/* <Grid item xs={12}>*/}
      {/*  <Button*/}
      {/*    variant={'contained'}*/}
      {/*    color={'primary'}*/}
      {/*    onClick={createCourse(state, enqueueSnackbar)}*/}
      {/*  >*/}
      {/*    Create Course*/}
      {/*  </Button>*/}
      {/* </Grid>*/}
      <Grid item/>
      <Grid item xs={12} md={10}>
        <Grid container spacing={4}>
          {courses.map((course) => (
            <Grid item xs={12} md={6} lg={4} key={course.id}>
              <Card>
                <CardContent>
                  <Grid container spacing={2}>
                    {editableFields.map(({field, label, disabled = false, type = 'string'}) => {
                      switch (type) {
                      case 'string':
                        return (
                          <Grid item xs={12} key={field}>
                            <TextField
                              disabled={disabled}
                              variant={'outlined'}
                              style={{width: '100%'}}
                              label={label}
                              value={course[field]}
                              onChange={updateField(course.id, field)}
                            />
                          </Grid>
                        );
                      case 'boolean':
                        return (
                          <Grid item xs={12} key={field}>
                            <FormControlLabel
                              value={course[field]}
                              control={
                                <Switch
                                  checked={course[field]}
                                  color={'primary'}
                                  onClick={updateField(course.id, field, true)}
                                />
                              }
                              label={label}
                              labelPlacement="end"
                            />
                          </Grid>
                        );
                      case 'datetime':
                        const date = new Date(course[field]);
                        return (
                          <Grid item xs={12} key={field}>
                            <MuiPickersUtilsProvider utils={DateFnsUtils}>
                              <KeyboardDatePicker
                                margin="normal"
                                label={label}
                                format="yyyy-MM-dd"
                                value={date}
                                onChange={updateField(course.id, field, false, true)}
                              />
                              <KeyboardTimePicker
                                margin="normal"
                                label="Time"
                                value={date}
                                onChange={updateField(course.id, field, false, true)}
                              />
                            </MuiPickersUtilsProvider>
                          </Grid>
                        );
                      }
                    })}
                  </Grid>
                </CardContent>
                <CardActionArea>
                  <Button
                    size={'small'}
                    color={'primary'}
                    variant={'contained'}
                    className={classes.button}
                    onClick={saveCourse(course.id)}
                  >
                    Save
                  </Button>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Grid>
    </Grid>
  );
}
