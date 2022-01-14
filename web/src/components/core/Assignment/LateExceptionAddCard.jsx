import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import {KeyboardDatePicker, KeyboardTimePicker, MuiPickersUtilsProvider} from '@material-ui/pickers';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import DateFnsUtils from '@date-io/date-fns';
import Autocomplete from '@material-ui/lab/Autocomplete';
import TextField from '@material-ui/core/TextField';
import CardActions from '@material-ui/core/CardActions';
import Button from '@material-ui/core/Button';
import SaveIcon from '@material-ui/icons/Save';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import {nonStupidDatetimeFormat} from '../../../utils/datetime';

const useStyles = makeStyles((theme) => ({
  datePicker: {
    marginRight: theme.spacing(2),
  },
  button: {
    marginRight: theme.spacing(1),
  },
}));

export default function LateExceptionAddCard({assignment, setReset}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [date, setDate] = useState(new Date(assignment.due_date));
  const [students, setStudents] = useState([]);
  const [selected, setSelected] = useState(null);

  React.useEffect(() => {
    axios.get(`/api/admin/students/list`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.students) {
        setStudents(data.students);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  const save = () => {
    if (selected === null) {
      enqueueSnackbar('No student selected', {variant: 'error'});
      return;
    }
    axios.post(`/api/admin/late-exceptions/update`, {
      assignment_id: assignment.id,
      user_id: selected.id,
      due_date: nonStupidDatetimeFormat(date),
    }).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
      setReset((prev) => ++prev);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  return (
    <Card>
      <CardContent>
        <Autocomplete
          getOptionLabel={(option) => option.netid}
          renderInput={(params) => <TextField {...params} label="Student" variant="outlined"/>}
          options={students}
          onChange={(_, v) => setSelected(v)}
        />
        <MuiPickersUtilsProvider utils={DateFnsUtils}>
          <KeyboardDatePicker
            className={classes.datePicker}
            margin="normal"
            label="Due Date"
            format="yyyy-MM-dd"
            value={date}
            onChange={(v) => setDate(v)}
          />
          <KeyboardTimePicker
            className={classes.datePicker}
            margin="normal"
            label="Time"
            value={date}
            onChange={(v) => setDate(v)}
          />
        </MuiPickersUtilsProvider>
      </CardContent>
      <CardActions>
        <Button
          className={classes.button}
          color={'primary'}
          variant={'contained'}
          size={'small'}
          startIcon={<SaveIcon/>}
          onClick={save}
        >
                    Add or Update
        </Button>
      </CardActions>
    </Card>
  );
}
