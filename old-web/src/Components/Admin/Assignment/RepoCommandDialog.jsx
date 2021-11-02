import React from 'react';

import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';

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
