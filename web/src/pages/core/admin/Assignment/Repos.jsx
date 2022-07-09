import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {useParams} from 'react-router-dom';

import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

import standardErrorHandler from '../../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import AssignmentReposTable from '../../../../components/core/Assignment/AssignmentReposTable';
import RepoCommandDialog from '../../../../components/core/Assignment/RepoCommandDialog';
import downloadTextFile from '../../../../utils/downloadTextFile';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  button: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
}));


export default function Repos() {
  const classes = useStyles();
  const match = useParams();
  const {enqueueSnackbar} = useSnackbar();
  const [repos, setRepos] = useState([]);
  const [assignment, setAssignment] = useState({});
  const [reset, setReset] = useState(0);

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
  }, [reset]);

  return (
    <Grid container spacing={2} justifyContent={'center'} alignItems={'center'}>
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
          Download Repo Metadata
        </Button>
        <RepoCommandDialog
          repos={repos}
          assignment={assignment}
          className={classes.button}
        />
      </Grid>
      <Grid item xs={12} md={10}>
        <AssignmentReposTable repos={repos} setReset={setReset}/>
      </Grid>
    </Grid>
  );
}
