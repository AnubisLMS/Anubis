import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import {useHistory} from 'react-router-dom';
import axios from 'axios';

import {DataGrid} from '@mui/x-data-grid';
import Paper from '@mui/material/Paper';
import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';

import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';

import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import VisibilityIcon from '@mui/icons-material/Visibility';

import green from '@mui/material/colors/green';
import grey from '@mui/material/colors/grey';

import standardStatusHandler from '../../../../utils/standardStatusHandler';
import ManagementIDEDialog from '../../../../components/core/AdminIDE/ManagementIDEDialog';
import standardErrorHandler from '../../../../utils/standardErrorHandler';

const useStyles = makeStyles((theme) => ({
  paper: {
    height: 700,
    padding: theme.spacing(1),
  },
  dialog: {
    padding: theme.spacing(1),
  },
  autocomplete: {
    width: 300,
    margin: theme.spacing(1),
  },
  buttonGrid: {
    margin: theme.spacing(1),
  },
}));

export default function Assignments() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [reset, setReset] = useState(0);

  const [open, setOpen] = React.useState(false);
  const [inputValue, setInputValue] = React.useState('');
  const [value, setValue] = React.useState('');
  const [students, setStudents] = React.useState([]); // List of students to select from in dropdown

  const [assignments, setAssignments] = useState([]);
  const history = useHistory();

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  React.useEffect(() => {
    axios.get('/api/admin/assignments/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.assignments) {
        setAssignments(data.assignments);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  React.useEffect(() => {
    axios.get('/api/admin/students/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.students) {
        setStudents(data.students.map((student) => student.netid));
      } else {
        enqueueSnackbar('Unable to fetch students', {variant: 'error'});
      }
    }).catch((error) => {
      enqueueSnackbar(error.toString(), {variant: 'error'});
    });
  }, [open]);

  const addAssignment = () => {
    axios.post('/api/admin/assignments/add').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.assignment) {
        setReset((prev) => ++prev);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const autogradeStudent = (net_id) => (params = {}) => {
    axios.get(`/api/admin/regrade/student/${net_id}`, {params}).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.session?.state === 'autograding') {
        enqueueSnackbar('Autograding student', {variant: 'success'});
        history.push(`/admin/autograde/${data.session.id}`);
      }
    }).catch((error) => {
      console.log(error); standardErrorHandler(enqueueSnackbar);
    });
  };

  const autograde = () => {
    autogradeStudent(value)();
    setOpen(false);
  };

  return (
    <div className={classes.root}>
      <Grid container justifyContent={'center'} alignItems={'center'}>
        <Grid item xs={12}>
          <Typography variant="h6">
            Anubis
          </Typography>
          <Typography variant={'subtitle1'} color={'textSecondary'}>
            Assignment Management
          </Typography>
        </Grid>
        <Grid container className={classes.buttonGrid} spacing={2} justifyContent={'left'} alignItems={'center'} >
          <Grid item xs='auto'>
            <Button variant={'contained'} color={'primary'} onClick={addAssignment}>
              Add Assignment
            </Button>
          </Grid>
          <Grid item xs='auto'>
            <Button
              onClick={handleClickOpen}
              variant={'contained'}
              color={'primary'}
            >
              Autograde Student
            </Button>
          </Grid>
          <Grid item xs='auto'>
            <ManagementIDEDialog/>
          </Grid>
        </Grid>
        <Grid item xs={8}>
          <Paper className={classes.paper}>
            <DataGrid columns={[
              {field: 'name', headerName: 'Assignment Name', width: 200},
              {field: 'hidden', headerName: 'Visibility', width: 110, renderCell: ({row}) => (
                <Tooltip title={
                  !row.hidden ? 'Visible to students' : 'Hidden to students'
                }>
                  {
                    !row.hidden ?
                      <VisibilityIcon style={{color: green[500]}}/> :
                      <VisibilityOffIcon style={{color: grey[500]}}/>
                  }
                </Tooltip>
              )},
              {field: 'release_date', headerName: 'Release Date', width: 170},
              {field: 'due_date', headerName: 'Due Date', width: 170},
            ]} rows={assignments} onRowClick={({row}) => history.push(`/admin/assignment/edit/${row.id}`)}/>
          </Paper>
        </Grid>
      </Grid>
      <Dialog className={classes.dialog} open={open} onClose={handleClose}>
        <DialogTitle>Autograde Student</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Select student to autograde:
          </DialogContentText>
        </DialogContent>
        <Autocomplete
          className={classes.autocomplete}
          value={value}
          onChange={(event, newValue) => {
            setValue(newValue);
          }}
          inputValue={inputValue}
          onInputChange={(event, newInputValue) => {
            setInputValue(newInputValue);
          }}
          options={students}
          renderInput={(params) => <TextField {...params} label="Student" variant='outlined'/>}
        />
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={autograde}>Autograde</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
