import React, {useState} from 'react';
import Redirect from 'react-router-dom/Redirect';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import makeStyles from '@material-ui/core/styles/makeStyles';
import {DataGrid} from '@material-ui/data-grid';
import Grid from '@material-ui/core/Grid';
import {Paper} from '@material-ui/core';

import standardStatusHandler from '../../Utils/standardStatusHandler';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import Typography from '@material-ui/core/Typography';
import clsx from 'clsx';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  paper: {
    flex: 1,
    padding: theme.spacing(1),
  },
  dataGridPaper: {
    height: 700,
  },
}));


const useColumns = () => ([
  {field: 'name', headerName: 'Assignment Name', width: 200},
  {field: 'due_date', headerName: 'Due Date', type: 'dateTime', width: 200},
  {field: 'id', headerName: 'ID', width: 150},
  {field: 'unique_code', headerName: 'Unique Code', width: 150},
]);

const sortModel = [
  {
    field: 'due_date',
    sort: 'desc',
  },
];

export default function Stats() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [assignments, setAssignments] = useState([]);
  const [selected, setSelected] = useState(null);
  const columns = useColumns();

  React.useEffect(() => {
    axios.get('/api/admin/assignments/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setAssignments(data.assignments);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  if (selected) {
    return <Redirect to={`/admin/stats/assignment?assignmentId=${selected.id}`}/>;
  }

  return (
    <Grid container spacing={4} justify={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Autograded Assignments
        </Typography>
      </Grid>
      <Grid item xs={12} md={8}>
        <Paper className={clsx(classes.paper, classes.dataGridPaper)}>
          <DataGrid
            sortModel={sortModel}
            columns={columns}
            rows={assignments}
            onRowClick={({row}) => setSelected(row)}
          />
        </Paper>
      </Grid>
    </Grid>
  );
}
