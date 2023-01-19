import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import {DataGrid} from '@mui/x-data-grid';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import EditIcon from '@mui/icons-material/Edit';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import TextField from '@mui/material/TextField';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import Autocomplete from '@mui/lab/Autocomplete';
import {AdapterDateFns} from '@mui/x-date-pickers/AdapterDateFns';
import {DesktopDateTimePicker} from '@mui/x-date-pickers/DesktopDateTimePicker';
import {LocalizationProvider} from '@mui/x-date-pickers/LocalizationProvider';
import Box from '@mui/material/Box';
import {nonStupidDatetimeFormat} from '../../../utils/datetime';

const useStyles = makeStyles((theme) => ({
  paper: {
    minHeight: 700,
    padding: theme.spacing(1),
  },
  button: {
    margin: theme.spacing(1),
  },
}));

const deleteReservation = (id, state, enqueueSnackbar) => {
  axios.delete(`/api/admin/reserve/delete/${id}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
      state.setReset((prev) => ++prev);
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};


const saveReservation = (reservation, state, enqueueSnackbar) => {
  reservation.start = nonStupidDatetimeFormat(reservation.start);
  reservation.end = nonStupidDatetimeFormat(reservation.end);
  axios.post(`/api/admin/reserve/save/${reservation.id}`, {reservation}).then((response) => {
    standardStatusHandler(response, enqueueSnackbar);
    state.setReset((prev) => ++prev);
  }).catch(standardErrorHandler(enqueueSnackbar));
};


const useColumns = (state, enqueueSnackbar) => ([
  {field: 'assignment', headerName: 'Assignment', width: 300, valueGetter: (params) => (params.row.assignment?.name)},
  {field: 'start', headerName: 'Start', width: 200, valueGetter: (params) => nonStupidDatetimeFormat(params.row.start)},
  {field: 'end', headerName: 'End', width: 200, valueGetter: (params) => nonStupidDatetimeFormat(params.row.end)},
  {field: 'active', headerName: 'Active', width: 100, renderCell: (params) => (
    <Tooltip title={params.row.active ? 'Reservation is currently active' : 'Reservation not is currently active'}>
      <IconButton>
        {params.row.active ? <CheckIcon color={'primary'}/> : <CloseIcon color={'error'}/>}
      </IconButton>
    </Tooltip>
  )},
  {field: 'edit', headerName: 'Edit', width: 120, renderCell: (params) => (
    <Button
      startIcon={<EditIcon/>}
      variant={'contained'}
      color={'primary'}
      onClick={() => state.setEdit(params.row)}
    >
      Edit
    </Button>
  )},
  {field: 'delete', headerName: 'Delete', width: 120, renderCell: (params) => (
    <Button
      startIcon={<DeleteForeverIcon/>}
      variant={'contained'}
      color={'error'}
      onClick={() => deleteReservation(params.row?.id, state, enqueueSnackbar)}
    >
      Delete
    </Button>
  )},
]);

const AddReservationDialog = ({setReset}) => {
  const {enqueueSnackbar} = useSnackbar();
  const [open, setOpen] = useState(false);
  const [assignments, setAssginments] = useState([]);
  const [selected, setSelected] = useState(null);

  React.useEffect(() => {
    axios.get('/api/admin/assignments/list').then((response) => {
      const data = standardStatusHandler(response);
      if (data.assignments) {
        setAssginments(data.assignments);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  return (
    <React.Fragment>
      <Button onClick={() => setOpen(true)} variant={'contained'} color={'primary'}>Add</Button>
      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>
          Add reserved time for assignment
        </DialogTitle>
        <DialogContent>
          <Autocomplete
            value={selected}
            onChange={(e, value) => setSelected(value)}
            options={assignments}
            sx={{width: 400, p: 1}}
            getOptionLabel={(option) => option.name}
            renderInput={(params) => <TextField {...params} label="Assignment"/>}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} variant={'contained'} color={'primary'} autoFocus>Cancel</Button>
          <Button
            disabled={selected === null}
            onClick={() => {
              axios.post(`/api/admin/reserve/add/${selected.id}`).then((response) => {
                standardStatusHandler(response, enqueueSnackbar);
                setReset((prev) => ++prev);
              }).catch(standardErrorHandler(enqueueSnackbar));
              setOpen(false);
            }}
            variant={'contained'}
            color={'primary'}
            autoFocus
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
};


const DatePicker = ({label, value, setValue}) => (
  <LocalizationProvider dateAdapter={AdapterDateFns} sx={{p: 1}}>
    <DesktopDateTimePicker
      margin="normal"
      label={label}
      ampm={false}
      inputFormat="yyyy-MM-dd HH:mm:ss"
      views={['year', 'day', 'hours', 'minutes', 'seconds']}
      value={value}
      onChange={setValue}
      renderInput={(params) => <TextField {...params} />}
    />
  </LocalizationProvider>
);

export default function Reservations() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [reservations, setReservations] = useState([]);
  const [reset, setReset] = useState([]);
  const [edit, setEdit] = useState(null);

  const pageState = {
    reservations, setReservations,
    reset, setReset,
    edit, setEdit,
  };

  React.useEffect(() => {
    axios.get('/api/admin/reserve/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        for (const reservation of data.reservations) {
          reservation.start = new Date(reservation.start.replace(/-/g, '/'));
          reservation.end = new Date(reservation.end.replace(/-/g, '/'));
        }
        setReservations(data.reservations);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  const columns = useColumns(pageState, enqueueSnackbar);

  return (
    <div className={classes.root}>
      <Dialog open={!!edit} onClose={() => setEdit(null)}>
        {!!edit && (
          <React.Fragment>
            <DialogTitle>
              Edit Reservation
            </DialogTitle>
            <DialogContent>
              <Box sx={{p: 1, m: 1}}>
                <DatePicker label={'Start'} value={edit.start} setValue={(value) => setEdit((prev) => {
                  prev.start = value; return {...prev};
                })}/>
              </Box>
              <Box sx={{p: 1, m: 1}}>
                <DatePicker label={'End'} value={edit.end} setValue={(value) => setEdit((prev) => {
                  prev.end = value; return {...prev};
                })}/>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button autoFocus onClick={() => setEdit(null)} variant={'contained'} color={'primary'}>Cancel</Button>
              <Button onClick={() => {
                saveReservation(edit, pageState, enqueueSnackbar);
                setEdit(null);
              }} variant={'contained'} color={'primary'}>Save</Button>
            </DialogActions>
          </React.Fragment>
        )}
      </Dialog>
      <Grid container spacing={4} justifyContent={'center'} alignItems={'center'}>
        <Grid item xs={12}>
          <Typography variant="h6">
              Anubis
          </Typography>
          <Typography variant={'subtitle1'} color={'textSecondary'}>
              Reserve IDE Time
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <AddReservationDialog className={classes.button} setReset={setReset}/>
        </Grid>
        <Grid item/>
        <Grid item xs={12} md={12} lg={10}>
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <Paper className={classes.paper}>
                <div style={{height: 700}}>
                  <DataGrid
                    pagination
                    className={classes.dataGrid}
                    columns={columns}
                    rows={reservations}
                  />
                </div>
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </div>
  );
}
