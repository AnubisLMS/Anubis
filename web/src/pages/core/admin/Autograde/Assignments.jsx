import React, {useState} from 'react';
import clsx from 'clsx';
import axios from 'axios';
import {Redirect} from 'react-router-dom';
import {useSnackbar} from 'notistack';

import {DataGrid} from '@material-ui/data-grid';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';

import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  paper: {
    // flex: 1,
    padding: theme.spacing(1),
  },
  dataGridPaper: {
    height: 700,
  },
  dataGrid: {
    height: '100%',
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

export default function Assignments() {
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
    return <Redirect to={`/admin/autograde/assignment/${selected.id}`}/>;
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
      <Grid item xs={12} sm={10} md={8}>
        <Paper className={clsx(classes.dataGridPaper, classes.paper)}>
          <DataGrid
            className={classes.dataGrid}
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
