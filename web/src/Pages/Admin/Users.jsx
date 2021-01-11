import React, {useState} from 'react';
import {Redirect} from 'react-router-dom';

import makeStyles from '@material-ui/core/styles/makeStyles';
import {DataGrid} from '@material-ui/data-grid/';
import CircularProgress from '@material-ui/core/CircularProgress';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';

import useGet from '../../hooks/useGet';


const useStyles = makeStyles((theme) => ({
  paper: {
    margin: theme.spacing(1),
    maxWidth: 750,
  },
  dataGrid: {
    minHeight: 400,
    minWidth: 750,
  },
}));

const columns = [
  {field: 'id', hide: true},
  {field: 'netid', headerName: 'netid'},
  {field: 'name', headerName: 'Name', width: 130},
  {field: 'github_username', headerName: 'Github Username', width: 150},
  {field: 'is_admin', headerName: 'Admin', type: 'string'},
  {field: 'is_superuser', headerName: 'Superuser', type: 'string', width: 120},
];

export default function Users() {
  const classes = useStyles();
  const [{loading, error, data}] = useGet('/api/admin/students/list');
  const [selected, setSelected] = useState(null);

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  if (selected !== null) {
    return (
      <Redirect to={`/user?userId=${selected}`}/>
    );
  }

  const {students: rows} = data;

  console.log(rows);

  return (
    <Grid container spacing={2} justify={'center'} alignItems={'center'} direction={'column'}>
      <Grid item xs key={'user-table'}>
        <Paper className={classes.paper}>
          <div className={classes.dataGrid}>
            <DataGrid rows={rows} columns={columns} pageSize={10} onRowClick={({row: {id}}) => setSelected(id)}/>
          </div>
        </Paper>
      </Grid>
    </Grid>
  );
}
