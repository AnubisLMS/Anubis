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

import standardErrorHandler from '../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../utils/standardStatusHandler';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  input: {
    display: 'none',
  },
}));


const uploadFiles = (state, enqueueSnackbar) => () => {
  const {files, setFiles, setOpen, setReset} = state;

  for (const file of files) {
    const form = new FormData();
    form.append('image', file);

    axios.post('/api/admin/static/upload', form, {
      headers: {'Content-Type': 'multipart/form-data'},
    }).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setReset((prev) => ++prev);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }

  setOpen(false);
  setFiles([]);
};

export default function FileUploadDialog({setReset}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [open, setOpen] = useState(false);
  const [files, setFiles] = useState([]);

  const handleClose = () => setOpen(false);
  const handleOpen = () => setOpen(true);

  const state = {
    setReset,
    open, setOpen,
    files, setFiles,
  };

  return (
    <React.Fragment>
      <Button
        color={'primary'}
        variant={'contained'}
        onClick={handleOpen}
      >
        Upload Files
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">Upload new file</DialogTitle>
        <DialogContent>
          <List>
            {files.map((file) => (
              <ListItem key={file.name}>
                <ListItemText
                  primary={file.name}
                />
              </ListItem>
            ))}
          </List>
          <input
            className={classes.input}
            id="upload-input"
            type="file"
            multiple
            onChange={(e) => setFiles([...e.target.files])}
          />
          <label htmlFor="upload-input">
            <Button variant="contained" color="primary" component="span">
              Select Files
            </Button>
          </label>
        </DialogContent>
        <DialogActions>
          <Button
            autoFocus
            color="primary"
            variant="contained"
            disabled={files.length === 0}
            onClick={uploadFiles(state, enqueueSnackbar)}
          >
            Upload
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}
