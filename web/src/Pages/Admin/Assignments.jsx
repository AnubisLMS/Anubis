import React, {useState} from 'react';

import Grid from '@material-ui/core/Grid';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import makeStyles from '@material-ui/core/styles/makeStyles';
import TextField from '@material-ui/core/TextField';
import DateFnsUtils from '@date-io/date-fns';
import {KeyboardDatePicker, KeyboardTimePicker, MuiPickersUtilsProvider} from '@material-ui/pickers';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';
import CardActionArea from '@material-ui/core/CardActionArea';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import CodeOutlinedIcon from '@material-ui/icons/CodeOutlined';
import ManagementIDEDialog from '../../Components/Admin/IDE/ManagementIDEDialog';


const useStyles = makeStyles((theme) => ({
  root: {
    minWidth: 275,
  },
  bullet: {
    display: 'inline-block',
    margin: '0 2px',
    transform: 'scale(0.8)',
  },
  title: {
    fontSize: 14,
  },
  pos: {
    marginBottom: 12,
  },
  button: {
    margin: theme.spacing(1),
  },
}));

const editableFields = [
  {field: 'name', label: 'Assignment Name'},
  {field: 'github_classroom_url', label: 'Github Classroom URL'},
  {field: 'pipeline_image', label: 'Pipeline Image', disabled: true},
  {field: 'unique_code', label: 'Unique Code', disabled: true},
  {field: 'hidden', label: 'Hidden', type: 'boolean'},
  {field: 'ide_enabled', label: 'Theia Enabled', type: 'boolean'},
  {field: 'release_date', label: 'Release Date', type: 'datetime'},
  {field: 'due_date', label: 'Due Date', type: 'datetime'},
  {field: 'grace_date', label: 'Grace Date', type: 'datetime'},
];

const nonStupidDatetimeFormat = (date) => (
  `${date.getFullYear()}-${date.getMonth()+1}-${date.getDate()} ` +
  `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`
);


export default function Assignments() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [assignments, setAssignments] = useState([]);
  const [edits, setEdits] = useState(0);
  const [reset, setReset] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);

  React.useEffect(() => {
    axios.get('/api/admin/assignments/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.assignments) {
        for (const assignment of data.assignments) {
          for (const field of editableFields) {
            if (field.type === 'datetime') {
              assignment[field.field] = new Date(assignment[field.field].replace(/-/g, '/'));
            }
          }
        }
        setAssignments(data.assignments);
      }
    }).catch((error) => enqueueSnackbar(error.toString(), {variant: 'error'}));
  }, [reset]);

  const updateField = (id, field, toggle = false, datetime = false) => (e) => {
    if (!e) {
      return;
    }

    for (const assignment of assignments) {
      if (assignment.id === id) {
        if (toggle) {
          assignment[field] = !assignment[field];
          break;
        }

        if (datetime) {
          assignment[field] = e;
          break;
        }

        assignment[field] = e.target.value.toString();
        break;
      }
    }
    setAssignments(assignments);
    setEdits((state) => ++state);
  };

  const saveAssignment = (id) => () => {
    for (const assignment of assignments) {
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
    }

    enqueueSnackbar('An error occurred', {variant: 'error'});
  };

  return (
    <Grid container spacing={1} justify={'center'} alignItems={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Assignment Management
        </Typography>
      </Grid>
      <Grid item xs={12}>
        <Button
          variant={'contained'}
          color={'primary'}
          startIcon={<CodeOutlinedIcon/>}
          onClick={() => setDialogOpen(true)}
        >
          Management IDE
        </Button>
      </Grid>
      <ManagementIDEDialog open={dialogOpen} handleDialogToggle={() => setDialogOpen((prev) => !prev)}/>
      {assignments.map((assignment) => (
        <Grid item xs={8} key={assignment.id}>
          <Card>
            <CardContent>
              <Grid container spacing={2}>
                {editableFields.map(({field, label, disabled = false, type = 'string'}) => {
                  switch (type) {
                  case 'string':
                    return (
                      <Grid item xs={12} md={6} key={field}>
                        <TextField
                          fullWidth
                          disabled={disabled}
                          variant={'outlined'}
                          label={label}
                          value={assignment[field]}
                          onChange={updateField(assignment.id, field)}
                        />
                      </Grid>
                    );
                  case 'boolean':
                    return (
                      <Grid item xs={12} key={field}>
                        <FormControlLabel
                          value={assignment[field]}
                          control={
                            <Switch
                              checked={assignment[field]}
                              color={'primary'}
                              onClick={updateField(assignment.id, field, true)}
                            />
                          }
                          label={label}
                          labelPlacement="end"
                        />
                      </Grid>
                    );
                  case 'datetime':
                    return (
                      <Grid item xs={12} key={field}>
                        <MuiPickersUtilsProvider utils={DateFnsUtils}>
                          <KeyboardDatePicker
                            margin="normal"
                            label={label}
                            format="yyyy-MM-dd"
                            value={assignment[field]}
                            onChange={updateField(assignment.id, field, false, true)}
                          />
                          <KeyboardTimePicker
                            margin="normal"
                            label="Time"
                            value={assignment[field]}
                            onChange={updateField(assignment.id, field, false, true)}
                          />
                        </MuiPickersUtilsProvider>
                      </Grid>
                    );
                  }
                })}
              </Grid>
            </CardContent>
            <CardActionArea>
              <Button
                size={'small'}
                color={'primary'}
                variant={'contained'}
                className={classes.button}
                onClick={saveAssignment(assignment.id)}
              >
                Save
              </Button>
            </CardActionArea>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}
