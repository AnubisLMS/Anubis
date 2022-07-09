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

import VisibilityIcon from '@mui/icons-material/Visibility';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';

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


const toggleSuperuser = (id, {setStudents, setEdits}, enqueueSnackbar) => () => {
  axios.get(`/api/admin/students/toggle-superuser/${id}`).then((response) => {
    if (standardStatusHandler(response, enqueueSnackbar)) {
      setStudents((students) => {
        for (const student of students) {
          if (student.id === id) {
            student.is_superuser = !student.is_superuser;
          }
        }
        return students;
      });
      setEdits((state) => ++state);
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};

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
]);

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
      return;
    }

    if (searched === null && students.length > 0) {
      return setRows(students);
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
