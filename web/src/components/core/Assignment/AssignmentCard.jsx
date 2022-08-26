import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {Link} from 'react-router-dom';
import clsx from 'clsx';

import {AdapterDateFns} from '@mui/x-date-pickers/AdapterDateFns';
import {LocalizationProvider} from '@mui/x-date-pickers/LocalizationProvider';
import {DesktopDateTimePicker} from '@mui/x-date-pickers/DesktopDateTimePicker';
import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import TextField from '@mui/material/TextField';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import Button from '@mui/material/Button';
import CardActions from '@mui/material/CardActions';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';
import Autocomplete from '@mui/lab/Autocomplete';

import SaveIcon from '@mui/icons-material/Save';
import EditIcon from '@mui/icons-material/Edit';
import RefreshIcon from '@mui/icons-material/Refresh';
import VisibilityIcon from '@mui/icons-material/Visibility';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PeopleIcon from '@mui/icons-material/People';

import standardErrorHandler from '../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import RegradeWarning from './RegradeWarning';
import DescriptionEditorDialog from './DescriptionEditorDialog';


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
                      getOptionLabel={(option) => option.title}
                      renderInput={(params) => <TextField {...params} label={label} variant="outlined"/>}
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
                    <LocalizationProvider dateAdapter={AdapterDateFns}>
                      <DesktopDateTimePicker
                        className={classes.datePicker}
                        margin="normal"
                        label={label}
                        format="yyyy-MM-dd hh:mm:ss"
                        value={assignment[field]}
                        onChange={updateField(assignment.id, field, false, true)}
                        renderInput={(params) => <TextField {...params} />}
                      />
                    </LocalizationProvider>
                  </Grid>
                );
              }
            })}
            <Grid item xs={12}>
              <Tooltip title={'Reload grading progress'}>
                <IconButton color={'primary'} onClick={() => setReset((prev) => ++prev)} size="large">
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
            color={'secondary'}
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
            startIcon={<EditIcon/>}
            className={clsx(classes.buttonRight, classes.button)}
            component={Link}
            to={`/admin/assignment/questions/${assignment.id}`}
          >
            Edit Questions
          </Button>
          <DescriptionEditorDialog
            assignment={assignment}
            updateField={updateField}
            saveAssignment={saveAssignment}
            className={classes.button}
          />
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
