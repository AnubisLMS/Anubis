import React from 'react';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';


const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
}));

export default function RepoCommandDialog({repos = [], assignment = {}}) {
  const [open, setOpen] = React.useState(false);
  const [http, setHttp] = React.useState(false);

  const handleClickOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  return (
    <div>
      <Button variant="contained" color="primary" onClick={handleClickOpen}>
        View Clone Command
      </Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogContent>
          <FormControlLabel
            control={
              <Switch
                checked={http}
                onChange={() => setHttp(!http)}
                name="http"
                color="primary"
              />
            }
            label={http ? 'http' : 'ssh'}
          />
          <p>
            mkdir -p &apos;{assignment?.name}&apos; <br/>
            cd &apos;{assignment?.name}&apos; <br/>
            {repos.map(({url, ssh, netid}) => (
              <div key={netid}>
                git clone {http ? url : ssh} {netid}
              </div>
            ))}
          </p>
        </DialogContent>
      </Dialog>
    </div>
  );
}
