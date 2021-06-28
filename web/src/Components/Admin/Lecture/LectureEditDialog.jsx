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
}));


const uploadLecture = (state, enqueueSnackbar) => () => {
  const {
    lecture,
    file, setFile,
    number, setNumber,
    title, setTitle,
    setOpen,
    setReset,
  } = state;

  if (file !== null) {
    const form = new FormData();
    form.append('image', file);

    axios.post(`/api/admin/lecture/save/${lecture.id}`, form, {
      params: {number, title, description: ''},
      headers: {'Content-Type': 'multipart/form-data'},
    }).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setReset((prev) => ++prev);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  } else {
    axios.post(`/api/admin/lecture/save/${lecture.id}`, {}, {
      params: {number, title, description: ''},
    }).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setReset((prev) => ++prev);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }

  // reset everything
  setOpen(null);
  setFile(null);
  setTitle('');
  setNumber(1);
};

export default function FileUploadDialog({setReset, open, setOpen, lecture}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [file, setFile] = useState(null);
  const [number, setNumber] = useState(1);
  const [title, setTitle] = useState('');

  const handleClose = () => setOpen(null);

  useEffect(() => {
    setNumber(lecture?.number ?? 1);
    setTitle(lecture?.title ?? '');
  }, [lecture]);

  const state = {
    lecture,
    setReset,
    open, setOpen,
    file, setFile,
    title, setTitle,
    number, setNumber,
  };

  return (
    <React.Fragment>
      <Dialog
        open={open}
        onClose={handleClose}
      >
        <DialogTitle id="alert-dialog-title">Upload file</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Lecture Number"
            className={classes.field}
            type="number"
            InputLabelProps={{
              shrink: true,
            }}
            variant="outlined"
            value={number}
            onChange={(e) => setNumber(e.target.value)}
          />
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
