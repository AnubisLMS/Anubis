import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {Redirect} from 'react-router-dom';

import {DataGrid} from '@material-ui/data-grid';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import makeStyles from '@material-ui/core/styles/makeStyles';
import IconButton from '@material-ui/core/IconButton';
import Tooltip from '@material-ui/core/Tooltip';
import Typography from '@material-ui/core/Typography';
import Autocomplete from '@material-ui/lab/Autocomplete';
import TextField from '@material-ui/core/TextField';

import CheckOutlinedIcon from '@material-ui/icons/Check';
import CancelIcon from '@material-ui/icons/Cancel';

import useQuery from '../../hooks/useQuery';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import {NotInterested} from '@material-ui/icons';

const useStyles = makeStyles((theme) => ({
  paper: {
    minHeight: 700,
    padding: theme.spacing(1),
  },
  dataGrid: {
    height: '100%',
  },
  searchPaper: {
    flex: 1,
    padding: theme.spacing(1),
  },
  autocomplete: {
    paddingBottom: theme.spacing(1),
    paddingLeft: theme.spacing(1),
    paddingRight: theme.spacing(1),
  },
}));

const useColumns = () => ([
  {field: 'netid', headerName: 'Netid'},
  {field: 'name', headerName: 'Name', width: 130},
  {
    field: 'submission',
    headerName: 'Submitted',
    width: 150,
    renderCell: (params) => (
      <Tooltip title={params.value === null ? 'No Submission' : 'Submitted'}>
        <IconButton style={{color: params.value === null ? 'red' : 'green'}}>
          {params.value === null ? <CancelIcon/> : <CheckOutlinedIcon/>}
        </IconButton>
      </Tooltip>
    ),
  },
  {
    field: 'build_passed', headerName: 'Build Passed', width: 150,
    renderCell: (params) => (
      <React.Fragment>
        {params.row.submission !== null ? (
          <Tooltip title={params.value ? 'Build Succeeded' : 'Build Failed'}>
            <IconButton style={{color: params.value ? 'green' : 'yellow'}}>
              {params.value ? <CheckOutlinedIcon/> : <CancelIcon/>}
            </IconButton>
          </Tooltip>
        ) : (
          <Tooltip title={'No Submission'}>
            <IconButton style={{color: 'grey'}}>
              <NotInterested/>
            </IconButton>
          </Tooltip>
        )}

      </React.Fragment>
    ),
  },
  {
    field: 'tests_passed', headerName: 'Tests Passed', width: 150,
    renderCell: (params) => `${params.row.tests_passed}/${params.row.total_tests}`,
  },
]);


export default function AssignmentStats() {
  const query = useQuery();
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [assignment, setAssignment] = useState(null);
  const [students, setStudents] = useState([]);
  const [stats, setStats] = useState([]);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pageSize, setPageSize] = useState(10);
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState(null);
  const [searched, setSearched] = useState(null);
  const columns = useColumns();

  React.useEffect(() => {
    axios.get('/api/admin/students/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setStudents(data.students);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  React.useEffect(() => {
    setLoading(true);
    const offset = pageSize * (page - 1);
    const limit = pageSize;
    axios.get(
      `/api/admin/stats/assignment/${query.get('assignmentId')}`,
      {params: {limit, offset}},
    ).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);

      setStats((state) => {
        let j = 0;
        while (state.length < offset + limit) {
          state.push({id: j++});
        }
        let i = 0;
        for (let k = offset; k < offset + limit; ++k) {
          state[k] = data.stats[i++];
        }
        return [...state];
      });

      setLoading(false);
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [page, pageSize]);

  React.useEffect(() => {
    setRows([...stats]);
  }, [stats]);

  React.useEffect(() => {
    axios.get(`/api/admin/assignments/get/${query.get('assignmentId')}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);

      if (data) {
        setAssignment(data.assignment);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  React.useEffect(() => {
    if (!searched) {
      return setRows(stats);
    }

    axios.get(`/api/admin/stats/for/${assignment.id}/${searched.id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setRows([data.stats]);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [searched]);

  if (selected) {
    return <Redirect to={`/admin/stats/submission?assignmentId=${assignment.id}&netid=${selected.id}`}/>;
  }

  return (
    <Grid container spacing={2} justify={'center'} alignItems={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Assignment Autograde Results
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Results for {assignment?.name}
        </Typography>
      </Grid>
      <Grid item xs={12} md={4} key={'search'}>
        <Paper className={classes.searchPaper}>
          <div className={classes.autocomplete}>
            <Autocomplete
              blurOnSelect
              fullWidth={false}
              options={students}
              getOptionLabel={(option) => option.name}
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
      <Grid item/>
      <Grid item xs={12} md={10} lg={8}>
        <Paper className={classes.paper}>
          <DataGrid
            className={classes.dataGrid}
            loading={loading}
            rowCount={students.length}
            columns={columns}
            rows={rows}
            page={page}
            pageSize={pageSize}
            rowsPerPageOptions={[10, 15]}
            onPageChange={(params) => setPage(params.page)}
            onPageSizeChange={(params) => setPageSize(params.pageSize)}
            onRowClick={({row}) => setSelected(row)}
          />
        </Paper>
      </Grid>
    </Grid>
  );
}
