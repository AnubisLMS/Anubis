import React from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import Delete from '@mui/icons-material/Delete';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';


export default function DeleteAssignmentDialog({assignmentId, setRedirect}) {
  const [open, setOpen] = React.useState(false);
  const [confirm, setConfirm] = React.useState(false);
  const {enqueueSnackbar} = useSnackbar();

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const deleteAssignment = () => {
    axios.delete(`/api/admin/assignments/delete/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      handleClose();
      setConfirm(false);
      if (data) {
        setRedirect(`/admin/assignments`);
      }
    }).catch(standardErrorHandler);
  };

  return (
    <div>
      <Button variant="contained" color='error' onClick={handleClickOpen} startIcon={<Delete/>}>
        Delete
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
      >
        <DialogTitle>Are you very sure?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Deleting this assignment will delete all the submissions, and
            repositories. This is an extremely destructive action. It cannot be
            easily undone - if at all.
          </DialogContentText>
          <FormControlLabel
            control={
              <Switch
                checked={confirm}
                onChange={(_, v) => setConfirm(v)}
              />
            }
            labelPlacement={'end'}
            label={<i>Yes I confirm I would like to delete this assignment</i>}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary" variant={'contained'}>
            Cancel
          </Button>
          <Button onClick={deleteAssignment} color='error' variant={'contained'} disabled={!confirm} autoFocus>
            Yes delete this assignment
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
