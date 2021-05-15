import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {useParams} from 'react-router-dom';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

import standardErrorHandler from '../../../Utils/standardErrorHandler';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import AssignmentReposTable from '../../../Components/Admin/Assignment/AssignmentReposTable';
import RepoCommandDialog from '../../../Components/Admin/Assignment/RepoCommandDialog';
import downloadTextFile from '../../../Utils/downloadTextFile';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  button: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
}));


export default function AssignmentRepos() {
  const classes = useStyles();
  const match = useParams();
  const {enqueueSnackbar} = useSnackbar();
  const [repos, setRepos] = useState([]);
  const [assignment, setAssignment] = useState({});

  const assignmentId = match?.assignmentId;

  useEffect(() => {
    axios.get(`/api/admin/assignments/repos/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.repos) {
        setRepos(data?.repos);
      }
      if (data?.assignment) {
        setAssignment(data?.assignment);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  return (
    <Grid container spacing={2} justify={'center'} alignItems={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Assignment Repos
        </Typography>
        <Button
          variant={'contained'}
          color={'primary'}
          onClick={() => downloadTextFile(
            `assignment-${assignment?.name}-repos.json`,
            JSON.stringify(repos, null, 2),
            'application/json',
          )}
          className={classes.button}
        >
          Download Repos
        </Button>
        <RepoCommandDialog
          repos={repos}
          assignment={assignment}
          className={classes.button}
        />
      </Grid>
      <Grid item xs={12} md={10}>
        <AssignmentReposTable repos={repos}/>
      </Grid>
    </Grid>
  );
}
