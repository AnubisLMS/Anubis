import React from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';
import Delete from '@material-ui/icons/Delete';

import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';


export default function DeleteAssignmentDialog({assignmentId}) {
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
        window.location = '/admin/assignments';
      }
    }).catch(standardErrorHandler);
  };

  return (
    <div>
      <Button variant="contained" color="secondary" onClick={handleClickOpen} startIcon={<Delete/>}>
        Delete Assignment
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
          <Button onClick={deleteAssignment} color="secondary" variant={'contained'} disabled={!confirm} autoFocus>
            Yes delete this assignment
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
