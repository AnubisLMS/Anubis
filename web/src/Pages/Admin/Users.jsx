import React, {useState} from 'react';
import clsx from 'clsx';

import makeStyles from '@material-ui/core/styles/makeStyles';
import {DataGrid} from '@material-ui/data-grid/';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Switch from '@material-ui/core/Switch';
import TextField from '@material-ui/core/TextField';
import SearchIcon from '@material-ui/icons/Search';
import InputAdornment from '@material-ui/core/InputAdornment';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import {Link} from 'react-router-dom';
import PersonIcon from '@material-ui/icons/Person';
import Fab from '@material-ui/core/Fab';
import {Tooltip} from '@material-ui/core';


const useStyles = makeStyles((theme) => ({
  paper: {
    padding: theme.spacing(1),
  },
  fullHeightWidth: {
    height: 700,
  },
  dataGrid: {
    height: '100%',
    display: 'flex',
  },
  search: {
    display: 'flex',
  },
  input: {
    marginLeft: theme.spacing(1),
    flex: 1,
    width: '100%',
  },
}));


const toggleAdmin = (id, {setStudents, setEdits}, enqueueSnackbar) => () => {
  axios.get(`/api/admin/students/toggle-admin/${id}`).then((response) => {
    if (standardStatusHandler(response, enqueueSnackbar)) {
      setStudents((students) => {
        for (const student of students) {
          if (student.id === id) {
            student.is_admin = !student.is_admin;
          }
        }
        return students;
      });
      setEdits((state) => ++state);
    }
  }).catch((error) => enqueueSnackbar(error.toString(), {variant: 'error'}));
};


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
  }).catch((error) => enqueueSnackbar(error.toString(), {variant: 'error'}));
};

const useColumns = (pageState, enqueueSnackbar) => ([
  {
    field: 'id',
    headerName: 'ID',
    renderCell: (params) => (
      <Fab
        size={'small'}
        color={'primary'}
        component={Link}
        to={`/admin/user?userId=${params.row.id}`}
      >
        <Tooltip title={params.row.netid}>
          <PersonIcon/>
        </Tooltip>
      </Fab>
    ),
  },
  {field: 'netid', headerName: 'netid'},
  {field: 'name', headerName: 'Name', width: 130},
  {field: 'github_username', headerName: 'Github Username', width: 200},
  {
    field: 'is_admin',
    headerName: 'Admin',
    renderCell: (params) => (
      <React.Fragment>
        <Switch
          checked={params.row.is_admin}
          color={'primary'}
          onClick={toggleAdmin(params.row.id, pageState, enqueueSnackbar)}
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
]);

export default function Users() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [reset, setReset] = useState(0);
  const [edits, setEdits] = useState(0);
  const [students, setStudents] = useState(null);
  const [selected, setSelected] = useState(null);
  const [searchText, setSearchText] = useState(null);
  const [rows, setRows] = useState([]);

  const pageState = {
    reset, setReset,
    students, setStudents,
    selected, setSelected,
    edits, setEdits,
    searchText, setSearchText,
    rows, setRows,
  };

  const columns = useColumns(pageState, enqueueSnackbar);

  React.useEffect(() => {
    axios.get('/api/admin/students/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.students) {
        setSelected(null);

        for (const student of data.students) {
          student.search = student.name.toLowerCase() +
            student.netid.toLowerCase() +
            student.github_username.toString() +
            student.id.toLowerCase();
        }

        setStudents(data.students);
        setRows(data.students);
      } else {
        enqueueSnackbar('Unable to fetch students', {variant: 'error'});
      }
    }).catch((error) => {
      enqueueSnackbar(error.toString(), {variant: 'error'});
    });
  }, [reset]);

  React.useEffect(() => {
    if (searchText === null) {
      return;
    }

    if (searchText === '') {
      setRows(students);
      return;
    }
    const lowerSearchText = searchText.toLowerCase();
    const filtered = students.filter((row) => (
      row.search.match(lowerSearchText)
    ));
    setRows(filtered);
  }, [searchText]);

  return (
    <Grid container spacing={2} justify={'center'} alignItems={'center'} style={{height: '100%'}}>
      <Grid item xs={12} md={6} key={'search'}>
        <Paper className={classes.paper}>
          <TextField
            color={'primary'}
            label={'Search users'}
            className={classes.input}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon/>
                </InputAdornment>
              ),
            }}
          />
        </Paper>
      </Grid>
      <Grid item xs={12} md={10} key={'user-table'} style={{height: '100%'}}>
        <Paper className={clsx(classes.paper, classes.fullHeightWidth)}>
          <div className={classes.dataGrid}>
            <DataGrid
              pagination
              pageSize={10}
              rowsPerPageOptions={[5, 10, 20]}
              rows={rows}
              columns={columns}
              filterModel={{
                items: [
                  {columnField: 'name', operatorValue: 'contains', value: ''},
                ],
              }}
              onRowClick={({row: {id}}) => setSelected(id)}
            />
          </div>
        </Paper>
      </Grid>
    </Grid>
  );
}
