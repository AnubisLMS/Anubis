import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {Link} from 'react-router-dom';

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
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

import SaveIcon from '@material-ui/icons/Save';
import EditIcon from '@material-ui/icons/Edit';
import RefreshIcon from '@material-ui/icons/Refresh';

import standardErrorHandler from '../../../Utils/standardErrorHandler';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import clsx from 'clsx';

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
}));

const regradeAssignment = (id, enqueueSnackbar, setReset) => {
  axios.get(`/api/admin/regrade/assignment/${id}`).then((response) => {
    standardStatusHandler(response, enqueueSnackbar);
    setReset((prev) => ++prev);
  }).catch(standardErrorHandler(enqueueSnackbar));
};

export default function AssignmentCard({assignment, editableFields, updateField, saveAssignment}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [progress, setProgress] = useState('');
  const [reset, setReset] = useState(0);
  const [warningOpen, setWarningOpen] = useState(false);

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
      <Dialog
        open={warningOpen}
        onClose={() => setWarningOpen(false)}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          Are you sure you want to proceed?
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            A regrade can take a very long time to complete. Please verify that
            you would like to proceed with the regrade.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            color="primary"
            onClick={() => setWarningOpen(false)}
            variant={'contained'}
            size={'small'}
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              setWarningOpen(false);
              regradeAssignment(assignment.id, enqueueSnackbar, setReset);
            }}
            style={{backgroundColor: yellow[500]}}
            variant={'contained'}
            size={'small'}
            autoFocus
          >
            Regrade
          </Button>
        </DialogActions>
      </Dialog>
      <Card className={classes.card}>
        <CardContent>
          <Grid container spacing={2}>
            {editableFields.map(({field, label, disabled = false, type = 'string'}) => {
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
              case 'boolean':
                return (
                  <Grid item xs={12} key={field}>
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
            to={`/admin/assignment/questions/${assignment.unique_code}`}
            startIcon={<EditIcon/>}
          >
            Edit Questions
          </Button>
          <Button
            size={'small'}
            color={'primary'}
            variant={'contained'}
            component={Link}
            to={`/admin/assignment/tests/${assignment.id}`}
            startIcon={<EditIcon/>}
          >
            Edit Tests
          </Button>
        </CardActions>
      </Card>
    </React.Fragment>
  );
}
