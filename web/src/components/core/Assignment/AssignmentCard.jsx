import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {Link} from 'react-router-dom';
import clsx from 'clsx';

import {KeyboardDatePicker, KeyboardTimePicker, MuiPickersUtilsProvider} from '@material-ui/pickers';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import DateFnsUtils from '@date-io/date-fns';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';
import Button from '@material-ui/core/Button';
import CardActions from '@material-ui/core/CardActions';
import yellow from '@material-ui/core/colors/yellow';
import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import Autocomplete from '@material-ui/lab/Autocomplete';

import SaveIcon from '@material-ui/icons/Save';
import EditIcon from '@material-ui/icons/Edit';
import RefreshIcon from '@material-ui/icons/Refresh';
import VisibilityIcon from '@material-ui/icons/Visibility';
import AccessTimeIcon from '@material-ui/icons/AccessTime';
import PeopleIcon from '@material-ui/icons/People';

import standardErrorHandler from '../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import RegradeWarning from './RegradeWarning';


const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  inline: {
    display: 'inline',
  },
  datePicker: {
    marginRight: theme.spacing(2),
  },
  button: {
    marginRight: theme.spacing(1),
  },
  buttonRight: {
    marginLeft: 'auto',
  },
  card: {
    marginTop: theme.spacing(2),
  },
  input: {
    width: 42,
  },
}));

const regradeAssignment = (id, enqueueSnackbar, setReset) => (params = {}) => {
  axios.get(`/api/admin/regrade/assignment/${id}`, {params}).then((response) => {
    standardStatusHandler(response, enqueueSnackbar);
    setReset((prev) => ++prev);
  }).catch(standardErrorHandler(enqueueSnackbar));
};

export default function AssignmentCard({assignment, editableFields, updateField, saveAssignment}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [images, setImages] = useState([]);
  const [progress, setProgress] = useState('');
  const [reset, setReset] = useState(0);
  const [warningOpen, setWarningOpen] = useState(false);
  const [jsonValues, setJsonValues] = useState(
    ...editableFields.filter(({type}) => type === 'json').map(({field}) => ({
      [field]: JSON.stringify(assignment[field]),
    })),
  );

  React.useEffect(() => {
    axios.get(`/api/admin/ide/images/list`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.images) {
        setImages(data.images);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  React.useEffect(() => {
    axios.get(`/api/admin/regrade/status/${assignment.id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.percent) {
        setProgress(data.percent);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  return (
    <React.Fragment>
      <RegradeWarning
        warningOpen={warningOpen}
        setWarningOpen={setWarningOpen}
        regradeAssignment={regradeAssignment(assignment?.id, enqueueSnackbar, setReset)}
      />

      <Card className={classes.card}>
        <CardContent>
          <Grid container spacing={2}>
            {editableFields.map(({field, label, disabled = false, type = 'string'}) => {
              // Based on Label
              switch (field) {
              case 'theia_image':
                return (
                  <Grid item xs={12} lg={6}>
                    <Autocomplete
                      fullWidth
                      value={assignment[field]}
                      onChange={(_, v) => updateField(assignment.id, field, false, false, true)(v)}
                      options={images}
                      getOptionLabel={(option) => option.label}
                      renderInput={(params) => <TextField {...params} label={label} variant="outlined" />}
                    />
                  </Grid>
                );
              }

              // Based on type
              switch (type) {
              case 'string':
                return (
                  <Grid item xs={12} lg={6} key={field}>
                    <TextField
                      fullWidth
                      disabled={disabled}
                      variant={'outlined'}
                      label={label}
                      value={assignment[field]}
                      onChange={updateField(assignment.id, field)}
                    />
                  </Grid>
                );
              case 'json':
                return (
                  <Grid item xs={12} lg={6} key={field}>
                    <TextField
                      fullWidth
                      disabled={disabled}
                      variant={'outlined'}
                      label={label}
                      value={jsonValues[field]}
                      onChange={(e) => {
                        setJsonValues((prev) => {
                          prev[field] = e.target.value;
                          return {...prev};
                        });
                        try {
                          const value = JSON.parse(e.target.value);
                          updateField(assignment.id, field, false, false, true)(value);
                        } catch (e) {
                        }
                      }}
                    />
                  </Grid>
                );
              case 'boolean':
                return (
                  <Grid item xs={12} md={6} key={field}>
                    <FormControlLabel
                      value={assignment[field]}
                      control={
                        <Switch
                          checked={assignment[field]}
                          color={'primary'}
                          onClick={updateField(assignment.id, field, true)}
                        />
                      }
                      label={label}
                      labelPlacement="end"
                    />
                  </Grid>
                );
              case 'datetime':
                return (
                  <Grid item xs={12} key={field}>
                    <MuiPickersUtilsProvider utils={DateFnsUtils}>
                      <KeyboardDatePicker
                        className={classes.datePicker}
                        margin="normal"
                        label={label}
                        format="yyyy-MM-dd"
                        value={assignment[field]}
                        onChange={updateField(assignment.id, field, false, true)}
                      />
                      <KeyboardTimePicker
                        className={classes.datePicker}
                        margin="normal"
                        label="Time"
                        value={assignment[field]}
                        onChange={updateField(assignment.id, field, false, true)}
                      />
                    </MuiPickersUtilsProvider>
                  </Grid>
                );
              }
            })}
            <Grid item xs={12}>
              <Tooltip title={'Reload grading progress'}>
                <IconButton color={'primary'} onClick={() => setReset((prev) => ++prev)}>
                  <RefreshIcon/>
                </IconButton>
              </Tooltip>
              <Typography className={classes.inline}>
                {progress}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
        <CardActions disableSpacing>
          <Button
            size={'small'}
            color={'primary'}
            variant={'contained'}
            onClick={saveAssignment(assignment.id)}
            className={classes.button}
            startIcon={<SaveIcon/>}
          >
            Save
          </Button>
          <Button
            size={'small'}
            style={{backgroundColor: yellow[500]}}
            variant={'contained'}
            className={classes.button}
            onClick={() => setWarningOpen(true)}
            startIcon={<RefreshIcon/>}
          >
            Regrade
          </Button>
          <Button
            size={'small'}
            color={'primary'}
            variant={'contained'}
            className={clsx(classes.buttonRight, classes.button)}
            component={Link}
            to={`/admin/assignment/questions/${assignment.id}`}
            startIcon={<EditIcon/>}
          >
            Edit Questions
          </Button>
          <Button
            size={'small'}
            color={'primary'}
            variant={'contained'}
            className={classes.button}
            component={Link}
            to={`/admin/assignment/tests/${assignment.id}`}
            startIcon={<EditIcon/>}
          >
            Edit Tests
          </Button>
          <Button
            size={'small'}
            color={'primary'}
            variant={'contained'}
            className={classes.button}
            component={Link}
            to={`/admin/assignment/late-exceptions/${assignment.id}`}
            startIcon={<AccessTimeIcon/>}
          >
            Late Exceptions
          </Button>
          <Button
            size={'small'}
            color={'primary'}
            variant={'contained'}
            className={classes.button}
            component={Link}
            to={`/admin/assignment/groups/${assignment.id}`}
            startIcon={<PeopleIcon/>}
          >
            Groups
          </Button>
          <Button
            size={'small'}
            color={'primary'}
            variant={'contained'}
            className={classes.button}
            component={Link}
            to={`/admin/assignment/repos/${assignment.id}`}
            startIcon={<VisibilityIcon/>}
          >
            View Repos
          </Button>
        </CardActions>
      </Card>
    </React.Fragment>
  );
}
