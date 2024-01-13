import React, {useState} from 'react';
import clsx from 'clsx';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {Link} from 'react-router-dom';

import {DataGrid} from '@mui/x-data-grid';
import makeStyles from '@mui/styles/makeStyles';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import Switch from '@mui/material/Switch';
import TextField from '@mui/material/TextField';
import Fab from '@mui/material/Fab';
import Tooltip from '@mui/material/Tooltip';
import Autocomplete from '@mui/lab/Autocomplete';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Box from '@mui/material/Box';

import VisibilityIcon from '@mui/icons-material/Visibility';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';

import {SuperDeletePvc} from '../../../components/core/Profile/DeletePvc.jsx';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';

const useStyles = makeStyles((theme) => ({
  paper: {
    flex: 1,
    padding: theme.spacing(1),
  },
  dataGridPaper: {
    height: 900,
  },
  dataGrid: {
    height: '100%',
    display: 'flex',
  },
  autocomplete: {
    paddingBottom: theme.spacing(1),
    paddingLeft: theme.spacing(1),
    paddingRight: theme.spacing(1),
  },
}));


const toggleField = (field) => (id, {setStudents, setEdits}, enqueueSnackbar) => () => {
  axios.get(`/api/super/students/toggle-${field}/${id}`).then((response) => {
    if (standardStatusHandler(response, enqueueSnackbar)) {
      setStudents((students) => {
        for (const student of students) {
          if (student.id === id) {
            let field_label = field;
            if (!(field_label in student)) {
              field_label = 'is_' + field;
            }
            student[field_label] = !student[field_label];
          }
        }
        return students;
      });
      setEdits((state) => ++state);
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};

const toggleSuperuser = toggleField('superuser');
const toggleDeveloper = toggleField('anubis_developer');
const toggleDisabled = toggleField('disabled');

const useColumns = (pageState, enqueueSnackbar) => () => ([
  {
    field: 'id',
    headerName: 'View',
    renderCell: (params) => (
      <Tooltip title={`View ${params.row.netid}`}>
        <Fab
          size={'small'}
          color={'primary'}
          component={Link}
          to={`/admin/user?userId=${params.row.id}`}
        >
          <VisibilityIcon/>
        </Fab>
      </Tooltip>
    ),
  },
  {field: 'netid', headerName: 'netid'},
  {field: 'name', headerName: 'Name', width: 150},
  {field: 'github_username', headerName: 'Github Username', width: 200},
  {field: 'source', headerName: 'Source', width: 100},
  {
    field: 'log_in_as',
    headerName: 'Log in as',
    width: 130,
    renderCell: (params) => (
      <Tooltip title={`Log in as ${params.row.netid}`}>
        <Fab
          size={'small'}
          style={{backgroundColor: 'yellow'}}
          onClick={() => {
            axios.get(`/api/admin/auth/token/${params.row.netid}`).then((response) => {
              const data = standardStatusHandler(response);
              if (data) {
                window.location.reload();
              }
            }).catch(standardErrorHandler(enqueueSnackbar));
          }}
        >
          <ExitToAppIcon/>
        </Fab>
      </Tooltip>
    ),
  },
  {
    field: 'disabled',
    headerName: 'Disabled',
    renderCell: (params) => (
      <React.Fragment>
        <Switch
          checked={params.row.disabled}
          color={'primary'}
          onClick={toggleDisabled(params.row.id, pageState, enqueueSnackbar)}
        />
      </React.Fragment>
    ),
    width: 150,
  },
  {
    field: 'is_anubis_developer',
    headerName: 'Developer',
    renderCell: (params) => (
      <React.Fragment>
        <Switch
          checked={params.row.is_anubis_developer}
          color={'primary'}
          onClick={toggleDeveloper(params.row.id, pageState, enqueueSnackbar)}
        />
      </React.Fragment>
    ),
    width: 150,
  },
  {
    field: 'is_superuser',
    headerName: 'Superuser',
    renderCell: (params) => (
      <React.Fragment>
        <Switch
          checked={params.row.is_superuser}
          color={'primary'}
          onClick={toggleSuperuser(params.row.id, pageState, enqueueSnackbar)}
        />
      </React.Fragment>
    ),
    width: 150,
  },
  {
    field: 'Delete IDE Volume',
    headerName: 'Delete IDE Volume',
    renderCell: (params) => (
      <SuperDeletePvc id={`${params.row.id}`} netid={`${params.row.netid}`}/>
    ),
    width: 200,
  },
]);


function UserAdd({setReset}) {
  const [open, setOpen] = React.useState(false);
  const [netid, setNetid] = React.useState('');
  const [name, setName] = React.useState('');
  const {enqueueSnackbar} = useSnackbar();

  const close = () => {
    setOpen(false);
    setNetid('');
    setName('');
    setReset((prev) => ++prev);
  };

  return (
    <div>
      <Button variant="contained" color={'primary'} onClick={() => setOpen(true)}>
        Add Student
      </Button>
      <Dialog
        fullScreen={fullScreen}
        open={open}
        onClose={close}
        aria-labelledby="responsive-dialog-title"
      >
        <DialogTitle id="responsive-dialog-title">
          Add Student
        </DialogTitle>
        <DialogContent>
          <Box sx={{mt: 1, mb: 1}}>
            <TextField
              sx={{m: 0.5}}
              label="NetID"
              variant="outlined"
              value={netid}
              onChange={(e) => setNetid(e.target.value)}
            />
            <TextField
              sx={{m: 0.5}}
              label="Name"
              variant="outlined"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button autoFocus variant={'contained'} color={'primary'} onClick={close}>
            Cancel
          </Button>
          <Button variant={'contained'} color={'primary'} onClick={() => {
            axios.put(`/api/super/students/add`, {netid, name}).then((response) => {
              standardStatusHandler(response, enqueueSnackbar);
              close();
            }).catch(standardErrorHandler(enqueueSnackbar));
          }}>
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default function Users() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [reset, setReset] = useState(0);
  const [edits, setEdits] = useState(0);
  const [students, setStudents] = useState([]);
  const [searched, setSearched] = useState(null);
  const [rows, setRows] = useState([]);

  const pageState = {
    reset, setReset,
    students, setStudents,
    searched, setSearched,
    edits, setEdits,
    rows, setRows,
  };

  const columns = useColumns(pageState, enqueueSnackbar);

  React.useEffect(() => {
    axios.get('/api/super/students/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.students) {
        setSearched(null);

        for (const student of data.students) {
          student.search = student.name.toLowerCase() +
            student.netid.toLowerCase() +
            (student.github_username ?? '').toString() +
            student.id.toLowerCase();
        }

        setStudents(data.students);
      } else {
        enqueueSnackbar('Unable to fetch students', {variant: 'error'});
      }
    }).catch((error) => {
      enqueueSnackbar(error.toString(), {variant: 'error'});
    });
  }, [reset]);

  React.useEffect(() => {
    if (students.length === 0) {
      return undefined;
    }

    if (searched === null && students.length > 0) {
      setRows(students);
      return undefined;
    }

    setRows([searched]);
  }, [searched]);

  React.useEffect(() => {
    setRows(students);
  }, [students]);

  return (
    <Grid container spacing={2} justifyContent={'center'} alignItems={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          User Management
        </Typography>
      </Grid>
      <UserAdd setReset={setReset}/>
      <Grid item xs={12} md={4} key={'search'}>
        <Paper className={classes.paper}>
          <div className={classes.autocomplete}>
            <Autocomplete
              blurOnSelect
              fullWidth={false}
              options={students}
              getOptionLabel={(option) => `${option.netid} ${option.name}`}
              onChange={(_, value) => setSearched(value)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label={'Search users'}
                />
              )}
            />
          </div>
        </Paper>
      </Grid>
      <Grid item xs={12} md={10} key={'user-table'}>
        <Paper className={clsx(classes.paper, classes.dataGridPaper)}>
          <div className={classes.dataGrid}>
            <DataGrid
              pagination
              pageSize={15}
              rowsPerPageOptions={[5, 10, 20]}
              rows={rows}
              columns={columns()}
              filterModel={{
                items: [
                  {columnField: 'name', operatorValue: 'contains', value: ''},
                ],
              }}
            />
          </div>
        </Paper>
      </Grid>
    </Grid>
  );
}
