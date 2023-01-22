import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {Link} from 'react-router-dom';

import Grid from '@mui/material/Grid';
import makeStyles from '@mui/styles/makeStyles';
import TextField from '@mui/material/TextField';
import CardActionArea from '@mui/material/CardActionArea';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import yellow from '@mui/material/colors/yellow';
import EditIcon from '@mui/icons-material/Edit';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import Autocomplete from '@mui/lab/Autocomplete';

import AuthContext from '../../../context/AuthContext';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';

import BatchAddInput from '../Users/BatchAddInput';


const useStyles = makeStyles((theme) => ({
  button: {
    margin: theme.spacing(1),
  },
}));

export default function CourseCard({course, _disabled, editableFields, updateField, saveCourse}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [images, setImages] = useState([]);

  const [isBatchModalOpen, setIsBatchModalOpen] = useState(false);

  React.useEffect(() => {
    axios.get(`/api/admin/ide/images/list`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.images) {
        setImages(data.images);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);


  const onBatchAddStudents = (students, create_pvc) => {
    console.log('students', students, create_pvc);
    setIsBatchModalOpen(false);
    axios.post('/api/admin/courses/batch/students', {students: students, create_pvc: create_pvc}).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  return (
    <Card>
      <CardContent>

        <BatchAddInput onAdd={onBatchAddStudents} isOpen={isBatchModalOpen}/>
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
                    getOptionLabel={(option) => option.title}
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
                color={'secondary'}
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
                color={'secondary'}
                variant={'contained'}
                className={classes.button}
                onClick={() => setIsBatchModalOpen(true)}
              >
                { /** [TODO] Implement Batch Add Students */}
                Batch Add Students
              </Button>
              <Button
                size={'small'}
                startIcon={<EditIcon/>}
                color={'secondary'}
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
                  color={'secondary'}
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
