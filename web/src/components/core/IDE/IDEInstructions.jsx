import React from 'react';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import red from '@material-ui/core/colors/red';

export default function IDEInstructions() {
  const [open, setOpen] = React.useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <div>
      <Button color="primary" onClick={handleClickOpen}>
        View Instructions
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        fullWidth
        maxWidth={'md'}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{'Anubis IDE Instructions'}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Please consider your cloud IDE sessions as temporary. The IDE server you are allocated is being
            limited in: storage,
            networking capabilities, memory resources and cpu resources. When you create a Cloud IDE session, we
            clone exactly what is in your github repo into your Cloud IDE filesystem. When we stop and reclaim your
            Cloud IDE
            resources, we delete the Cloud IDE instance allocated to you. There is some witchcraft in the Cloud IDE
            instance that will automatically commit and push your work every 5 minutes. You should <i>not</i> rely
            on this exclusively.
          </DialogContentText>
          <DialogContentText>
            If you enable the persistent volume, your personal Anubis Cloud IDE volume will be mounted to
            /home/anubis for the duration of the session. Work here will be available the next time you launch
            a session with the persistent volume enabled. You are responsible for making sure that your work
            is backed up elsewhere. Data loss for these persistent volumes is not an excuse for late or incomplete
            work.
          </DialogContentText>
          <DialogContentText>
            Each session will last for a maximum of 6 hours. After that, the resources running your IDE will be
            reclaimed. When that happens, any un-pushed work will be lost.
          </DialogContentText>
          <DialogContentText>
            <div style={{color: red[500], display: 'inline'}}>
              By using this feature of Anubis, you are agreeing to accept the responsibility of making sure your work
              is saved. You are also agreeing not to attempt any form of abuse or hacking of any kind on our systems.
              We log <i>absolutely everything</i>.
            </div>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} variant={'contained'} color="primary" autoFocus>
            OK
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
