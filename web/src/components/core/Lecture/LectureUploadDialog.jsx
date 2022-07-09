import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import makeStyles from '@mui/styles/makeStyles';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import TextField from '@mui/material/TextField';
import {AdapterDateFns} from '@mui/x-date-pickers/AdapterDateFns';
import {LocalizationProvider} from '@mui/x-date-pickers/LocalizationProvider';
import {DesktopDatePicker} from '@mui/x-date-pickers/DesktopDatePicker';

import standardErrorHandler from '../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import {nonStupidDatetimeFormat} from '../../../utils/datetime';

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
    file, setFile,
    title, setTitle,
    postTime,
    setOpen,
    setReset,
  } = state;

  const form = new FormData();
  form.append('image', file);

  axios.post('/api/admin/lectures/upload', form, {
    params: {post_time: nonStupidDatetimeFormat(postTime), title, description: ''},
    headers: {'Content-Type': 'multipart/form-data'},
  }).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
      setReset((prev) => ++prev);
      setOpen(false);
      setFile(null);
      setTitle('');
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};

export default function FileUploadDialog({setReset}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState(null);
  const [postTime, setPostTime] = useState(new Date());
  const [title, setTitle] = useState('');

  const handleClose = () => setOpen(false);
  const handleOpen = () => setOpen(true);

  const state = {
    setReset,
    open, setOpen,
    file, setFile,
    title, setTitle,
    postTime, setPostTime,
  };

  return (
    <React.Fragment>
      <Button
        color={'primary'}
        variant={'contained'}
        onClick={handleOpen}
      >
        Upload Lecture
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">Upload file</DialogTitle>
        <DialogContent>

          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DesktopDatePicker
              className={classes.datePicker}
              margin="normal"
              label={'Post Time'}
              format="yyyy-MM-dd hh:mm:ss"
              value={postTime}
              onChange={(v) => setPostTime(v)}
              renderInput={(params) => <TextField {...params} />}
            />
          </LocalizationProvider>
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
            disabled={file === null}
            onClick={uploadLecture(state, enqueueSnackbar)}
          >
            Upload
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}
