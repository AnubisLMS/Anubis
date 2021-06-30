import React, {useEffect, useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import TextField from '@material-ui/core/TextField';

import standardErrorHandler from '../../../Utils/standardErrorHandler';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import DateFnsUtils from '@date-io/date-fns';
import {KeyboardDatePicker, KeyboardTimePicker, MuiPickersUtilsProvider} from '@material-ui/pickers';
import {nonStupidDatetimeFormat} from '../../../Utils/datetime';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  input: {
    display: 'none',
  },
  field: {
    margin: theme.spacing(1, 1),
  },
  datePicker: {
    marginRight: theme.spacing(2),
  },
}));


const uploadLecture = (state, enqueueSnackbar) => () => {
  const {
    lecture,
    file, setFile,
    postTime, setPostTime,
    title, setTitle,
    setOpen,
    setReset,
  } = state;

  const reset = () => {
    // reset everything
    setReset((prev) => ++prev);
    setOpen(null);
    setFile(null);
    setTitle('');
    setPostTime(null);
  };

  if (file !== null) {
    const form = new FormData();
    form.append('image', file);

    axios.post(`/api/admin/lectures/save/${lecture.id}`, form, {
      params: {post_time: nonStupidDatetimeFormat(postTime), title, description: ''},
      headers: {'Content-Type': 'multipart/form-data'},
    }).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        reset();
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  } else {
    axios.post(`/api/admin/lectures/save/${lecture.id}`, {}, {
      params: {post_time: nonStupidDatetimeFormat(postTime), title, description: ''},
    }).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        reset();
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }
};

export default function FileUploadDialog({setReset, open, setOpen, lecture}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [file, setFile] = useState(null);
  const [postTime, setPostTime] = useState(null);
  const [title, setTitle] = useState('');

  const handleClose = () => setOpen(null);

  useEffect(() => {
    setPostTime(new Date(lecture?.post_time ?? null));
    setTitle(lecture?.title ?? '');
  }, [lecture]);

  const state = {
    lecture,
    setReset,
    open, setOpen,
    file, setFile,
    title, setTitle,
    postTime, setPostTime,
  };

  return (
    <React.Fragment>
      <Dialog
        open={open}
        onClose={handleClose}
      >
        <DialogTitle id="alert-dialog-title">Upload file</DialogTitle>
        <DialogContent>
          <MuiPickersUtilsProvider utils={DateFnsUtils}>
            <KeyboardDatePicker
              className={classes.datePicker}
              margin="normal"
              label={'Post Time'}
              format="yyyy-MM-dd"
              value={postTime}
              onChange={(v) => setPostTime(v)}
            />
            <KeyboardTimePicker
              className={classes.datePicker}
              margin="normal"
              label="Time"
              value={postTime}
              onChange={(v) => setPostTime(v)}
            />
          </MuiPickersUtilsProvider>
          <TextField
            fullWidth
            className={classes.field}
            label={'Lecture Title'}
            variant={'outlined'}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <List>
            <ListItem key={'file'}>
              <ListItemText
                primary={file === null ? 'please select a file' : file?.name}
              />
            </ListItem>
          </List>
          <input
            className={classes.input}
            id="upload-input"
            type="file"
            onChange={(e) => {
              if (e.target.files.length > 0) {
                setFile(e.target.files[0]);
              }
            }}
          />
          <label htmlFor="upload-input">
            <Button variant="contained" color="primary" component="span">
              Select File
            </Button>
          </label>
        </DialogContent>
        <DialogActions>
          <Button
            autoFocus
            color="primary"
            variant="contained"
            onClick={uploadLecture(state, enqueueSnackbar)}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}
