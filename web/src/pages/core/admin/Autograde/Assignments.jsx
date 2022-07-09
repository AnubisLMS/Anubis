import React, {useState} from 'react';
import clsx from 'clsx';
import axios from 'axios';
import {useHistory} from 'react-router-dom';
import {useSnackbar} from 'notistack';

import {DataGrid} from '@mui/x-data-grid';
import makeStyles from '@mui/material/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';

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
  const history = useHistory();
  const columns = useColumns();

  React.useEffect(() => {
    axios.get('/api/admin/assignments/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setAssignments(data.assignments);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

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
            onRowClick={({row}) => history.push(`/admin/autograde/assignment/${row.id}`)}
          />
        </Paper>
      </Grid>
    </Grid>
  );
}
