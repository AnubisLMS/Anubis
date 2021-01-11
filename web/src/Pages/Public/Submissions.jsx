import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import {Redirect} from 'react-router-dom';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import Zoom from '@material-ui/core/Zoom';
import Typography from '@material-ui/core/Typography';
import useGet from '../../hooks/useGet';
import {SubmissionsTable} from '../../Components/Public/Submissions/SubmissionsTable';
import useQuery from '../../hooks/useQuery';
import Questions from '../../Components/Public/Questions/Questions';

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


export default function Submissions() {
  const classes = useStyles();
  const query = useQuery();
  const [{loading, error, data}] = useGet(
    `/api/public/submissions/`,
    {
      assignmentId: query.get('assignmentId'),
      courseId: query.get('courseId'),
      userId: query.get('userId'),
    },
  );

  const assignment_id = query.get('assignmentId');

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  function translateSubmission({assignment_name, assignment_due, commit, processed, state, created}) {
    return {
      assignmentName: assignment_name, assignmentDue: new Date(assignment_due), state: state,
      commitHash: commit, processed: processed, timeSubmitted: created.split(' ')[0],
      dateSubmitted: created.split(' ')[1], timeStamp: new Date(created),
    };
  }

  const rows = data.submissions
    .map(translateSubmission)
    .sort((a, b) => (a.timeStamp > b.timeStamp ? -1 : 1)); // sorts submissions in reverse chronological order

  return (
    <div className={classes.root}>
      <Grid
        container
        direction="row"
        justify="center"
        alignItems="center"
        spacing={6}
      >
        <Grid item xs={12}>
          <Typography variant="h6" className={classes.subtitle}>
            CS-UY 3224
          </Typography>
        </Grid>

        {/* Questions */}
        {!!assignment_id ? (
          <Grid item xs={12}>
            <Questions assignment_id={assignment_id}/>
          </Grid>
        ) : null}

        {/* Submissions subheading */}
        <Grid item xs={12}>
          <Typography variant="body1">
            Submissions
          </Typography>
        </Grid>

        {/* Table */}
        <Zoom in={true} timeout={200}>
          <Grid item xs>
            <SubmissionsTable rows={rows}/>
          </Grid>
        </Zoom>
      </Grid>
    </div>
  );
}
