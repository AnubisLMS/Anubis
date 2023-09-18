import React from 'react';
import {useSnackbar} from 'notistack';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContentText from '@mui/material/DialogContentText';

export default function KillAllSessions({state, stopAllSessions}) {
  const [open, setOpen] = React.useState(false);
  const {enqueueSnackbar} = useSnackbar();

  const close = () => {
    setOpen(false);
  };

  return (
    <div>
      <Button
        variant={'contained'}
        color={'error'}
        onClick={() => setOpen(true)}
      >
        Kill All Sessions
      </Button>
      <Dialog
        open={open}
        onClose={close}
      >
        <DialogTitle>
          Are you sure?
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Killing all student sessions is a very destructive action. Are you sure you would like to proceed?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button autoFocus variant={'contained'} color={'primary'} onClick={close}>
            Cancel
          </Button>
          <Button variant={'contained'} color={'error'} onClick={() => {
            stopAllSessions(state, enqueueSnackbar)();
            setOpen(false);
          }}>
            Now, I am become Death, the destroyer of worlds
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
