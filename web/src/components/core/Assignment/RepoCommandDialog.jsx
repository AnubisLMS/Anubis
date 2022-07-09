import React from 'react';

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';

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
