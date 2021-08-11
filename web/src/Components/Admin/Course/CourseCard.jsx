import React from 'react';
import {Link} from 'react-router-dom';

import Grid from '@material-ui/core/Grid';
import makeStyles from '@material-ui/core/styles/makeStyles';
import TextField from '@material-ui/core/TextField';
import CardActionArea from '@material-ui/core/CardActionArea';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import yellow from '@material-ui/core/colors/yellow';
import EditIcon from '@material-ui/icons/Edit';
import Switch from '@material-ui/core/Switch';

import AuthContext from '../../../Contexts/AuthContext';
import FormControlLabel from '@material-ui/core/FormControlLabel';


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
          {editableFields.map(({field, label, type = 'text', disabled = false}) => (
            <Grid item xs={12} key={field}>
              {type === 'text' && <TextField
                fullWidth
                disabled={disabled || _disabled}
                variant={'outlined'}
                label={label}
                value={course[field]}
                onChange={updateField(course.id, field)}
              />}
              {type === 'boolean' && <FormControlLabel
                value={course[field]}
                label={label}
                labelPlacement="end"
                control={
                  <Switch
                    checked={course[field]}
                    color={'primary'}
                    onClick={updateField(course.id, field, true)}
                  />
                }
              />}
            </Grid>
          ))}
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
