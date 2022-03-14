import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {useHistory, Redirect, useParams} from 'react-router-dom';

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
import NotInterested from '@material-ui/icons/NotInterested';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';
import AutogradeVisuals from '../../../../components/core/Visuals/AutogradeVisuals';
import Button from '@material-ui/core/Button';
import RefreshIcon from '@material-ui/icons/Refresh';
import ArchiveIcon from '@material-ui/icons/Archive';
import downloadTextFile from '../../../../utils/downloadTextFile';
import {nonStupidDatetimeFormat} from '../../../../utils/datetime';

const useStyles = makeStyles((theme) => ({
  paper: {
    height: 700,
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
    renderCell: ({row}) => (
      <React.Fragment>
        {row?.submission !== null ? (
          <Tooltip title={row?.build_passed ? 'Build Succeeded' : 'Build Failed'}>
            <IconButton style={{color: row?.build_passed ? 'green' : 'yellow'}}>
              {row?.build_passed ? <CheckOutlinedIcon/> : <CancelIcon/>}
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
    sortComparator: (v1, v2, cellParams1, cellParams2) =>
      cellParams1.value < cellParams2.value,
    renderCell: ({row}) => `${row?.tests_passed}/${row?.total_tests}`,
  },
]);


export default function Results() {
  const {assignmentId} = useParams();
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [assignment, setAssignment] = useState(null);
  const [students, setStudents] = useState([]);
  const [stats, setStats] = useState([]);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searched, setSearched] = useState(null);
  const [error, setError] = useState(null);
  const history = useHistory();
  const columns = useColumns();

  React.useEffect(() => {
    axios.get('/api/admin/students/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.students) {
        setStudents(data.students);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  React.useEffect(() => {
    setLoading(true);
    axios.get(
      `/api/admin/autograde/assignment/${assignmentId}`,
    ).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);

      if (!data) {
        setError(true);
        return;
      }

      if (data.stats) {
        setStats(data.stats);
      }

      setLoading(false);
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  React.useEffect(() => {
    setRows([...stats]);
  }, [stats]);

  React.useEffect(() => {
    axios.get(`/api/admin/assignments/get/${assignmentId}`).then((response) => {
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

    axios.get(`/api/admin/autograde/for/${assignment.id}/${searched.id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setRows([data.stats]);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [searched]);

  if (error) {
    history.push(`/error`);
  }

  const clearCache = () => {
    axios.get(`/api/admin/autograde/cache-reset/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        enqueueSnackbar(
          'Cache is reset. You will likely need to reload', {
            variant: 'warning',
            action: (
              <Button
                size="small"
                startIcon={<RefreshIcon/>}
                color={'primary'}
                variant={'contained'}
                onClick={() => window.location.reload(true)}
              >
                Reload
              </Button>
            ),
          });
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

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

        <Grid container spacing={1}>

          {/* Clear Cache button */}
          <Grid item>
            <Button
              variant={'contained'}
              color={'primary'}
              onClick={clearCache}
            >
              Clear Cache
            </Button>
          </Grid>

          {/* Reset questions icon */}
          <Grid item>
            <Button
              startIcon={<ArchiveIcon/>}
              color={'primary'}
              variant={'contained'}
              component={'a'}
              href={`/api/admin/questions/export/${assignmentId}`}
              download
            >
              Question Assignments (zip)
            </Button>
          </Grid>

          {/* Reset questions icon */}
          <Grid item>
            <Button
              startIcon={<ArchiveIcon/>}
              color={'primary'}
              variant={'contained'}
              onClick={() => downloadTextFile(
                `anubis-autograde-${assignment?.course_id}-${assignment?.name}` +
                `-${nonStupidDatetimeFormat(new Date())}.json`,
                JSON.stringify(stats),
                'application/json',
              )}
            >
              Autograde Data
            </Button>
          </Grid>

        </Grid>
      </Grid>
      <Grid item xs={12}>
        <AutogradeVisuals assignmentId={assignmentId}/>
      </Grid>
      <Grid item xs={12} md={4} key={'search'}>
        <Paper className={classes.searchPaper}>
          <div className={classes.autocomplete}>
            <Autocomplete
              blurOnSelect
              fullWidth={false}
              options={students}
              getOptionLabel={(option) => (`${option.netid} ${option.name}`)}
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
            onRowClick={({row}) => history.push(`/admin/autograde/submission?assignmentId=${assignment.id}&netid=${row.id}`)}
          />
        </Paper>
      </Grid>
    </Grid>
  );
}
