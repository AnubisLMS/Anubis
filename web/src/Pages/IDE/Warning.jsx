import React from 'react';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import red from "@material-ui/core/colors/red";

export default function Warning() {
  const [open, setOpen] = React.useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <div>
      <Button variant="contained" color="primary" onClick={handleClickOpen}>
        View Instructions
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        fullWidth
        maxWidth={"md"}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{"Anubis IDE Instructions"}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            This is an early version of the Anubis Cloud IDE platform. Please excuse any performance or
            stability issues while we work out the bugs.
          </DialogContentText>
          <DialogContentText id="alert-dialog-description">
            Before being able to create a Cloud IDE session, you will need to have created a repo for the assignment
            you would like to work on. Refer to the assignment PDF to find the github classroom link.
            To create a new session, go to the assignments tab and click the "Launch Cloud IDE" button. You will
            be taken back to this table while your Cloud IDE instance is being allocated to you.
          </DialogContentText>
          <DialogContentText id="alert-dialog-description">
            Your cloud IDE session is temporary. The IDE server you are allocated is being limited in: storage,
            networking capabilities, memory resources and cpu resources. When you create a Cloud IDE session, we
            clone exactly what is in your github repo into your Cloud IDE filesystem. When we stop and reclaim your
            Cloud IDE
            resources, we delete the Cloud IDE instance allocated to you. This means that the filesystem for your
            Cloud IDE system, including your work will be deleted forever. There is a robot user in the Cloud IDE
            instance that will automatically commit and push your work every 5 minutes. You should
            <i>not</i> rely on this exclusively.
          </DialogContentText>
          <DialogContentText id="alert-dialog-description">
            Each session will last for a maximum of 6 hours. After that, the resources running your IDE will be
            reclaimed. When that happens, any un-pushed work will be lost.
          </DialogContentText>
          <DialogContentText id="alert-dialog-description">
            <div style={{color: red[500], display: "inline"}}>
              By using this feature of Anubis, you are agreeing to accept the responsibility of making sure your work
              is saved. You are also agreeing not to attempt any form of abuse or hacking of any kind on our systems.
              We log <i>absolutely everything</i>.
            </div>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} variant={"contained"} color="primary" autoFocus>
            OK
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}