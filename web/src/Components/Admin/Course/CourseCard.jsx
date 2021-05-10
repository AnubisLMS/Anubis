import React, {useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import DateFnsUtils from '@date-io/date-fns';
import {KeyboardDatePicker, KeyboardTimePicker, MuiPickersUtilsProvider} from '@material-ui/pickers';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';
import CardActionArea from '@material-ui/core/CardActionArea';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import EditIcon from '@material-ui/icons/Edit';
import yellow from '@material-ui/core/colors/yellow';
import AuthContext from '../../../Contexts/AuthContext';
import {Link} from 'react-router-dom';


const useStyles = makeStyles((theme) => ({
  button: {
    margin: theme.spacing(1),
  },
}));

export default function CourseCard({course, _disabled, editableFields, updateField, saveCourse}) {
  const classes = useStyles();

  return (
    <Card>
      <CardContent>
        <Grid container spacing={2}>
          {editableFields.map(({field, label, disabled = false, type = 'string'}) => {
            switch (type) {
            case 'string':
              return (
                <Grid item xs={12} key={field}>
                  <TextField
                    disabled={disabled || _disabled}
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
                    disabled={disabled || _disabled}
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
                      disabled={disabled || _disabled}
                      label={label}
                      format="yyyy-MM-dd"
                      value={date}
                      onChange={updateField(course.id, field, false, true)}
                    />
                    <KeyboardTimePicker
                      margin="normal"
                      disabled={disabled || _disabled}
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
      {!_disabled ? (
        <AuthContext.Consumer>
          {(user) => (
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
              <Button
                size={'small'}
                startIcon={<EditIcon/>}
                style={{backgroundColor: yellow[500]}}
                variant={'contained'}
                className={classes.button}
                component={Link}
                to={`/admin/course/tas`}
              >
                Edit TAs
              </Button>
              {user.is_superuser && (
                <Button
                  size={'small'}
                  startIcon={<EditIcon/>}
                  style={{backgroundColor: yellow[500]}}
                  variant={'contained'}
                  className={classes.button}
                  component={Link}
                  to={`/admin/course/professors`}
                >
                  Edit Professors
                </Button>
              )}
            </CardActionArea>
          )}
        </AuthContext.Consumer>
      ) : null}
    </Card>
  );
}
