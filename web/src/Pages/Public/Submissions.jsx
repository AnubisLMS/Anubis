import React, {useState} from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import {SubmissionsTable} from '../../Components/Public/Submissions/SubmissionsTable';
import useQuery from '../../hooks/useQuery';
import Questions from '../../Components/Public/Questions/Questions';
import axios from 'axios';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import {useSnackbar} from 'notistack';
import AuthContext from '../../Contexts/AuthContext';

const useStyles = makeStyles({
  root: {
    flexGrow: 1,
  },
  table: {
    minWidth: 500,
  },
  headerText: {
    fontWeight: 600,
  },
  commitHashContainer: {
    width: 200,
    overflow: 'hidden',
  },
});

function translateSubmission({assignment_name, assignment_due, commit, processed, state, created, tests}) {
  const testsPassed = tests.filter((test) => test.result.passed).length;
  const totalTests = tests.length;

  return {
    assignmentName: assignment_name, assignmentDue: new Date(assignment_due), state: state,
    commitHash: commit, processed: processed, timeSubmitted: created.split(' ')[0],
    dateSubmitted: created.split(' ')[1], timeStamp: new Date(created), testsPassed, totalTests,
  };
}


export default function Submissions() {
  const classes = useStyles();
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [submissions, setSubmissions] = useState([]);
  const [user, setUser] = useState(null);

  const assignment_id = query.get('assignmentId');

  React.useEffect(() => {
    axios.get(`/api/public/submissions/`, {
      params: {
        assignmentId: query.get('assignmentId'),
        courseId: query.get('courseId'),
        userId: query.get('userId'),
      },
    }).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.submissions) {
        setSubmissions(data.submissions
          .map(translateSubmission)
          .sort((a, b) => (a.timeStamp > b.timeStamp ? -1 : 1)));
      }
      if (data?.user) {
        setUser(data.user);
      }
    }).catch((error) => enqueueSnackbar(error.toString(), {variant: 'error'}));
  }, []);

  return (
    <div className={classes.root}>
      <Grid container justify="center" spacing={4}>
        <Grid item xs={12}>
          <Typography variant="h6">
            Anubis
          </Typography>
          <Typography variant={'subtitle1'} color={'textSecondary'}>
            {user?.name}&apos;s Submissions
          </Typography>
        </Grid>

        <Grid item/>

        <Grid item xs={12} md={10}>
          <Grid container spacing={4}>
            {/* Questions */}
            {!!assignment_id ? (
              <Grid item xs={12}>
                <Questions assignment_id={assignment_id}/>
              </Grid>
            ) : null}

            {/* Table */}
            <Grid item xs>
              <SubmissionsTable rows={submissions}/>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </div>
  );
}
