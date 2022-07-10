import React, {useState} from 'react';
import axios from 'axios';
import {useParams} from 'react-router-dom';
import {useSnackbar} from 'notistack';
import ReactAce from 'react-ace';
import 'ace-builds/src-min-noconflict/mode-json';
import 'ace-builds/src-min-noconflict/theme-monokai';

import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Typography from '@mui/material/Typography';
import Switch from '@mui/material/Switch';
import CardContent from '@mui/material/CardContent';
import CardActionArea from '@mui/material/CardActionArea';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import FormControlLabel from '@mui/material/FormControlLabel';

import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';
import AssignmentReposTable from '../../../../components/core/Assignment/AssignmentReposTable';

const useStyles = makeStyles((theme) => ({
  paper: {
    height: 700,
    padding: theme.spacing(1),
  },
  editor: {
    width: '100%',
  },
}));


export default function GroupAssignment() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const {assignmentId} = useParams();
  const [assignment, setAssignment] = useState(null);
  const [reset, setReset] = useState(0);
  const [open, setOpen] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const [repos, setRepos] = useState([]);
  const [groups, setGroups] = useState('[\n  []\n]');

  React.useEffect(() => {
    axios.get(`/api/admin/assignments/get/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.assignment) {
        setAssignment(data.assignment);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  React.useEffect(() => {
    axios.get(`/api/admin/assignments/repos/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.repos) {
        setRepos(data?.repos);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  const resetRepos = () => {
    axios.delete(`/api/admin/assignments/reset-repos/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setReset((prev) => ++prev);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const assignGroups = () => {
    let groupData;
    try {
      groupData = JSON.parse(groups);
    } catch (e) {
      enqueueSnackbar('unable to parse json: ' + e.toString(), {variant: 'error'});
      return;
    }
    axios.post(`/api/admin/assignments/shared/${assignmentId}`, {groups: groupData}).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setReset((prev) => ++prev);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  if (assignment === null) {
    return <div/>;
  }

  return (
    <Grid container spacing={2} justifyContent={'center'} alignItems={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Assignment Groups for {assignment.name}
        </Typography>
      </Grid>
      <Grid item xs={12}>
        <Button variant={'contained'} color={'secondary'} onClick={() => setOpen(true)}>Reset Repos</Button>
        <Dialog
          open={open}
          onClose={() => {
            setOpen(false);
            setConfirm(false);
          }}
        >
          <DialogTitle>Are you sure?</DialogTitle>
          <DialogContent>
            <DialogContentText>
              This is an extremely destructive action. All repos for this assignment will be deleted
              from github. Submission data for the repos deleted will also be deleted from Anubis.
              This will result in lost data. The Anubis team may be able to recover lost submission
              and autograde data but will not be able to recover repos deleted from github.
              Please see the clone repos command to backup all the repos before doing this action.
            </DialogContentText>
            <DialogContentText>
              Please confirm that you understand the risks and want to continue to complete this action.
            </DialogContentText>
            <FormControlLabel
              value={confirm}
              onChange={(_, v) => setConfirm(v)}
              control={<Switch color={'secondary'}/>}
              label={<i>I understand what this action does, and want to continue anyway.</i>}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => {
              setOpen(false);
              setConfirm(false);
            }} variant={'contained'} color="primary" autoFocus>
              Cancel
            </Button>
            <Button onClick={() => {
              setOpen(false);
              setConfirm(false);
              resetRepos();
            }} variant={'contained'} color="secondary" disabled={!confirm}>
              Reset Repos
            </Button>
          </DialogActions>
        </Dialog>
      </Grid>

      <Grid item xs={12} md={10}>
        <Card>
          <CardContent>
            <ReactAce
              width={'100%'}
              mode="json"
              theme="monokai"
              value={groups}
              onChange={(v) => setGroups(v)}
            />
          </CardContent>
          <CardActionArea>
            <CardActions>
              <Button variant={'contained'} color={'primary'} onClick={assignGroups}>Assign Groups</Button>
            </CardActions>
          </CardActionArea>
        </Card>
      </Grid>
      <Grid item xs={12} md={10}>
        <AssignmentReposTable repos={repos} setReset={setReset}/>
      </Grid>
    </Grid>
  );
}

