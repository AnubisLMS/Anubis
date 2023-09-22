import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import {AdapterDateFns} from '@mui/x-date-pickers/AdapterDateFns';
import {LocalizationProvider} from '@mui/x-date-pickers/LocalizationProvider';
import {DesktopDateTimePicker} from '@mui/x-date-pickers/DesktopDateTimePicker';

import makeStyles from '@mui/styles/makeStyles';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Autocomplete from '@mui/lab/Autocomplete';
import TextField from '@mui/material/TextField';
import CardActions from '@mui/material/CardActions';
import Button from '@mui/material/Button';
import SaveIcon from '@mui/icons-material/Save';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import {nonStupidDatetimeFormat} from '../../../utils/datetime';
import Box from '@mui/material/Box';

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
        <Box sx={{pt: 1, pb: 1}}>
          <Autocomplete
            getOptionLabel={(option) => option.netid}
            renderInput={(params) => <TextField {...params} label="Student" variant="outlined"/>}
            options={students}
            onChange={(_, v) => setSelected(v)}
          />
        </Box>
        <Box sx={{pt: 1}}>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DesktopDateTimePicker
              className={classes.datePicker}
              margin="normal"
              label="Due Date"
              ampm={false}
              inputFormat="yyyy-MM-dd hh:mm:ss a"
              value={date}
              onChange={(v) => setDate(v)}
              renderInput={(params) => <TextField {...params} />}
            />
          </LocalizationProvider>
        </Box>
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
