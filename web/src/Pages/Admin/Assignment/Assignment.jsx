import React, {useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import {useSnackbar} from 'notistack';
import Typography from '@material-ui/core/Typography';
import ManagementIDEDialog from '../../../Components/Admin/IDE/ManagementIDEDialog';
import AssignmentCard from '../../../Components/Admin/Assignment/AssignmentCard';
import axios from 'axios';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import {nonStupidDatetimeFormat} from '../../../Utils/datetime';
import useQuery from '../../../hooks/useQuery';
import {useParams} from 'react-router-dom';
import {CircularProgress} from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
}));

const editableFields = [
  {field: 'name', label: 'Assignment Name'},
  {field: 'github_classroom_url', label: 'Github Classroom URL'},
  {field: 'theia_image', label: 'Theia Image'},
  {field: 'theia_options', label: 'Theia Options', type: 'json'},
  {field: 'pipeline_image', label: 'Pipeline Image', disabled: true},
  {field: 'unique_code', label: 'Unique Code', disabled: true},
  {field: 'hidden', label: 'Hidden', type: 'boolean'},
  {field: 'accept_late', label: 'Accept Late Submissions', type: 'boolean'},
  {field: 'ide_enabled', label: 'Theia Enabled', type: 'boolean'},
  {field: 'autograde_enabled', label: 'Autograde Enabled', type: 'boolean'},
  {field: 'release_date', label: 'Release Date', type: 'datetime'},
  {field: 'due_date', label: 'Due Date', type: 'datetime'},
  {field: 'grace_date', label: 'Grace Date', type: 'datetime'},
];

export default function Assignment() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [assignment, setAssignment] = useState(null);
  const [reset, setReset] = useState(0);
  const {assignmentId} = useParams();

  React.useEffect(() => {
    axios.get(`/api/admin/assignments/get/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.assignment) {
        for (const field of editableFields) {
          if (field.type === 'datetime') {
            console.log(field.field);
            data.assignment[field.field] = new Date(data.assignment[field.field].replace(/-/g, '/'));
          }
        }
        setAssignment(data.assignment);
      }
    }).catch((error) => enqueueSnackbar(error.toString(), {variant: 'error'}));
  }, [reset]);

  const updateField = (id, field, toggle = false, datetime = false, json = false) => (e) => {
    if (!e) {
      return;
    }

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

  return (
    <Grid container spacing={2} justify={'center'} alignItems={'center'}>
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
      <Grid item xs={12} sm={10} md={8} key={assignment.id}>
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
