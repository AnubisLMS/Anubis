import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
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
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Autocomplete from '@material-ui/lab/Autocomplete';

import AuthContext from '../../../context/AuthContext';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';


const useStyles = makeStyles((theme) => ({
  button: {
    margin: theme.spacing(1),
  },
}));

export default function CourseCard({course, _disabled, editableFields, updateField, saveCourse}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [images, setImages] = useState([]);

  React.useEffect(() => {
    axios.get(`/api/admin/ide/images/list`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.images) {
        setImages(data.images);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  return (
    <Card>
      <CardContent>
        <Grid container spacing={2}>
          {editableFields.map(({field, label, type = 'text', disabled = false}) => {
            switch (field) {
            case 'theia_default_image':
              return (
                <Grid item xs={12} key={field}>
                  <Autocomplete
                    fullWidth
                    value={course[field]}
                    onChange={(_, v) => updateField(course.id, field, false, false, true)(v)}
                    options={images}
                    getOptionLabel={(option) => option.label}
                    renderInput={(params) => <TextField {...params} label={label} variant="outlined" />}
                  />
                </Grid>
              );
            }
            switch (type) {
            case 'text':
              return (
                <Grid item xs={12} key={field}>
                  <TextField
                    fullWidth
                    disabled={disabled || _disabled}
                    variant={'outlined'}
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
                    label={label}
                    labelPlacement="end"
                    control={
                      <Switch
                        checked={course[field]}
                        color={'primary'}
                        onClick={updateField(course.id, field, true)}
                      />
                    }
                  />
                </Grid>
              );
            }
            return null;
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
                to={`/admin/course/students`}
              >
                Edit Students
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
