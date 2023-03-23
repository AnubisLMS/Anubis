import React, {useState, useEffect} from 'react';
import axios from 'axios';
import {Redirect, useParams} from 'react-router-dom';
import {useSnackbar} from 'notistack';

import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import DeleteAssignmentDialog from '../../../../components/core/Assignment/DeleteAssignmentDialog';
import ManagementIDEDialog from '../../../../components/core/AdminIDE/ManagementIDEDialog';
import AssignmentCard from '../../../../components/core/Assignment/AssignmentCard';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import {nonStupidDatetimeFormat} from '../../../../utils/datetime';
import standardErrorHandler from '../../../../utils/standardErrorHandler';


const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
}));

const editableFields = [
  {title: 'Assignment Controls'},
  {field: 'name', label: 'Assignment Name'},
  {field: 'github_template', label: 'Github Template (ex: AnubisLMS/xv6)'},
  {field: 'theia_image', label: 'IDE Docker Image'},
  {field: 'theia_options', label: 'IDE Options JSON', type: 'json'},
  {field: 'pipeline_image', label: 'Autograde Docker Image'},
  {field: 'unique_code', label: 'Unique Code'},
  {field: 'hidden', label: 'Hidden', type: 'boolean'},
  {field: 'github_repo_required', label: 'Github Repos Required', type: 'boolean'},
  {field: 'accept_late', label: 'Accept Late Submissions', type: 'boolean'},
  {field: 'ide_enabled', label: 'IDEs Enabled', type: 'boolean'},
  {field: 'hide_due_date', label: 'Hide Due Date', type: 'boolean'},
  {field: 'autograde_enabled', label: 'Autograde Enabled', type: 'boolean'},
  {field: 'email_notifications_enabled', label: 'Email Notifications Enabled', type: 'boolean'},
  {field: 'release_date', label: 'Release Date', type: 'datetime'},
  {field: 'due_date', label: 'Due Date', type: 'datetime'},
  {field: 'grace_date', label: 'Grace Date', type: 'datetime'},
  {divider: true},
  {title: 'Beta Settings'},
  {field: 'shell_autograde_repo', label: 'Shell Autograde Repo (ex: os3224/exercises)'},
  {field: 'shell_autograde_exercise_path', label: 'Shell Exercise Path (ex: subdirectory/exercise.py)'},
  {field: 'shell_autograde_enabled', label: 'Shell Autograde Enabled', type: 'boolean'},
  {button: 'Sync Exercise Github', onClick: (enqueueSnackbar, assignmentId) => () => {
    axios.get(`/api/admin/assignments/shell/sync/${assignmentId}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
    }).catch(standardErrorHandler(enqueueSnackbar));
  }},
  {divider: true},
];

export default function Assignment() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [assignment, setAssignment] = useState(null);
  const [reset, setReset] = useState(0);
  const [redirect, setRedirect] = useState(null);
  const {assignmentId} = useParams();

  useEffect(() => {
    axios.get(`/api/admin/assignments/get/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.assignment) {
        for (const field of editableFields) {
          if (field.type === 'datetime') {
            data.assignment[field.field] = new Date(data.assignment[field.field].replace(/-/g, '/'));
          }
        }
        setAssignment(data.assignment);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  const updateField = (id, field, toggle = false, datetime = false, json = false) => (e) => {
    if (toggle) {
      assignment[field] = !assignment[field];
    } else if (datetime) {
      assignment[field] = e;
    } else if (json) {
      assignment[field] = e;
    } else {
      assignment[field] = e.target.value.toString();
    }

    setAssignment({...assignment});
  };

  const saveAssignment = (id) => () => {
    if (assignment.id === id) {
      const conv_assignment = {
        ...assignment,
        release_date: nonStupidDatetimeFormat(assignment.release_date),
        due_date: nonStupidDatetimeFormat(assignment.due_date),
        grace_date: nonStupidDatetimeFormat(assignment.grace_date),
      };
      axios.post(`/api/admin/assignments/save`, {assignment: conv_assignment}).then((response) => {
        standardStatusHandler(response, enqueueSnackbar);
      }).catch((error) => enqueueSnackbar(error.toString(), {variant: 'error'}));
      return;
    }

    enqueueSnackbar('An error occurred', {variant: 'error'});
  };

  if (assignment === null) {
    return <CircularProgress/>;
  }

  if (redirect) {
    return (
      <Redirect to={redirect}/>
    );
  }

  return (
    <Grid container spacing={2} justifyContent={'center'} alignItems={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Assignment Management
        </Typography>
      </Grid>
      <Grid item xs={12}>
        <ManagementIDEDialog/>
      </Grid>
      <Grid item xs={12}>
        <DeleteAssignmentDialog
          assignmentId={assignmentId}
          setRedirect={setRedirect}
        />
      </Grid>
      <Grid item xs={12} md={10} key={assignment.id}>
        <AssignmentCard
          assignment={assignment}
          saveAssignment={saveAssignment}
          editableFields={editableFields}
          updateField={updateField}
        />
      </Grid>
    </Grid>
  );
}
