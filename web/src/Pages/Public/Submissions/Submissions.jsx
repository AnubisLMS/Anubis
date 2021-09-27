import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import {Redirect} from 'react-router-dom';
import axios from 'axios';

import {DataGrid} from '@material-ui/data-grid';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';

import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import CancelIcon from '@material-ui/icons/Cancel';
import green from '@material-ui/core/colors/green';
import red from '@material-ui/core/colors/red';

import SubmissionRow from './SubmissionRow/SubmissionRow';
import useQuery from '../../../hooks/useQuery';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import Questions from '../../../Components/Public/Questions/Questions';
import StandardLayout from '../../../Components/Layouts/StandardLayout';

const useStyles = makeStyles((theme) => ({
  paper: {
    height: 700,
    padding: theme.spacing(1),
  },
}));

function translateSubmission({id, assignment_name, assignment_due, commit, processed, state, created, tests}) {
  return {
    assignment_name, assignment_due, commit, created, tests,
    id, assignmentDue: new Date(assignment_due), state: state,
    processed: processed, timeStamp: new Date(created),
  };
}


const useColumns = () => ([
  {field: 'id', hide: true},
  {field: 'assignment_name', headerName: 'Assignment Name', width: 200},
  {
    field: 'commit', headerName: 'Commit Hash', width: 150, renderCell: ({row}) => (
      row?.commit && row.commit.substring(0, 10)
    ),
  },
  {
    field: 'tests_passed', headerName: 'Tests Passed', width: 150, renderCell: ({row}) => (
      row?.tests && `${row.tests.filter((test) => test.result.passed).length}/${row.tests.length}`
    ),
  },
  {
    field: 'processed', headerName: 'Processed', width: 150, renderCell: ({row}) => (
      <React.Fragment>
        {row.processed ?
          <CheckCircleIcon style={{color: green[500]}}/> :
          <CancelIcon style={{color: red[500]}}/>}
      </React.Fragment>
    ),
  },
  {
    field: 'on_time', headerName: 'On Time', width: 150, renderCell: ({row}) => (
      <React.Fragment>
        {(row?.timeStamp && row.timeStamp <= row.assignmentDue) ?
          <CheckCircleIcon style={{color: green[500]}}/> :
          <CancelIcon style={{color: red[500]}}/>}
      </React.Fragment>
    ),
  },
  {
    field: 'timeStamp', headerName: 'Timestamp', width: 250, renderCell: ({row}) => (
      row.created
    ),
  },
]);


export default function Submissions() {
  const classes = useStyles();
  const query = useQuery();
  const columns = useColumns();
  const {enqueueSnackbar} = useSnackbar();
  const [rows, setRows] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rowCount, setRowCount] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [redirect, setRedirect] = useState(null);

  const assignmentId = query.get('assignmentId');
  const courseId = query.get('courseId');
  const userId = query.get('userId');

  React.useEffect(() => {
    setLoading(true);
    axios.get(`/api/public/submissions/`, {
      params: {
        assignmentId, courseId, userId,
        limit: pageSize,
        offset: page * pageSize,
      },
    }).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.total) {
        setRowCount(data?.total);
      }
      if (data?.submissions) {
        let prev;
        if (rows.length === 0) {
          prev = new Array(data?.total);
          for (let i = 0; i < prev.length; ++i) {
            prev[i] = {id: i};
          }
        } else {
          prev = rows;
        }

        const translation = data.submissions.map(translateSubmission);
        for (let i = page * pageSize; i < (page * pageSize) + translation.length; ++i) {
          prev[i] = translation[i - (page * pageSize)];
        }

        setRows([...prev]);
      }
      if (data?.user) {
        setUser(data.user);
      }
      setLoading(false);
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [pageSize, page]);

  console.log(rows);

  if (redirect !== null) {
    return <Redirect to={redirect}/>;
  }

  return (
    <StandardLayout title={`Submissions`}>
      <Grid container spacing={4}>

        {/* Questions */}
        {!!assignmentId ? (
          <Grid item xs={12}>
            <Questions assignment_id={assignmentId}/>
          </Grid>
        ) : null}

        {/* Table */}
        {rows.map((row, index) => (
          <SubmissionRow {... row} key={`${row.commit}-${index}`} />
        ))}
      </Grid>
    </StandardLayout>

  );
}
