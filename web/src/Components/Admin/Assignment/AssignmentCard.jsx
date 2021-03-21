import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import DateFnsUtils from '@date-io/date-fns';
import {KeyboardDatePicker, KeyboardTimePicker, MuiPickersUtilsProvider} from '@material-ui/pickers';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';
import Button from '@material-ui/core/Button';
import CardActions from '@material-ui/core/CardActions';
import SaveIcon from '@material-ui/icons/Save';
import EditIcon from '@material-ui/icons/Edit';
import {Link} from 'react-router-dom';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  datePicker: {
    marginRight: theme.spacing(2),
  },
  button: {
    margin: theme.spacing(1),
  },
  buttonRight: {
    marginLeft: 'auto',
  },
  card: {
    marginTop: theme.spacing(2),
  },
}));

export default function AssignmentCard({assignment, editableFields, updateField, saveAssignment}) {
  const classes = useStyles();

  return (
    <Card className={classes.card}>
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
                      className={classes.datePicker}
                      margin="normal"
                      label={label}
                      format="yyyy-MM-dd"
                      value={assignment[field]}
                      onChange={updateField(assignment.id, field, false, true)}
                    />
                    <KeyboardTimePicker
                      className={classes.datePicker}
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
      <CardActions disableSpacing>
        <Button
          size={'small'}
          color={'primary'}
          variant={'contained'}
          onClick={saveAssignment(assignment.id)}
          startIcon={<SaveIcon/>}
        >
          Save
        </Button>
        <Button
          size={'small'}
          color={'primary'}
          variant={'contained'}
          className={classes.buttonRight}
          component={Link}
          to={`/admin/assignment/questions/${assignment.unique_code}`}
          startIcon={<EditIcon/>}
        >
          Edit Questions
        </Button>
      </CardActions>
    </Card>
  );
}
