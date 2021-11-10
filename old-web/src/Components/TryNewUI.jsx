import React from 'react';
import Cookies from 'universal-cookie';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import useMediaQuery from '@material-ui/core/useMediaQuery';
import {useTheme} from '@material-ui/core/styles';


export default function TryNewUI() {
  const cookies = new Cookies();
  const [open, setOpen] = React.useState(false);
  const [checked, setChecked] = React.useState(false);
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <div>
      <Dialog
        fullScreen={fullScreen}
        open={open}
        onClose={() => setOpen(false)}
        aria-labelledby="responsive-dialog-title"
      >
        <DialogTitle id="responsive-dialog-title">Anubis is getting a new website!</DialogTitle>
        <DialogContent>
          <DialogContentText>
            We are excited to begin rolling out our new UI for users to try. This new interface
            is a complete overhaul from the old. Keep in mind this is still a beta version
            of the new website. If you run into any issues, switch back to the old UI.
            Clear your cookies if you are having issues switching back.
          </DialogContentText>
          <DialogContentText>
            Please understand that you are accepting a certain amount of risk by
            trying a beta version of the website. If you would like to report any bugs,
            you can do so on the issues page of the github repo.
          </DialogContentText>
          <FormControlLabel
            checked={checked}
            onChange={() => setChecked(!checked)}
            control={<Checkbox color="primary"/>}
            label={<i>I agree to participate in the beta.</i>}
          />
        </DialogContent>
        <DialogActions>
          <Button autoFocus onClick={() => setOpen(false)} color="primary" variant={'contained'}>
            Cancel
          </Button>
          <Button
            disabled={!checked}
            color="primary"
            variant={'contained'}
            onClick={() => {
              cookies.set('web', 'new', {path: '/'});
              setTimeout(() => {
                window.history.pushState('Anubis', 'Anubis', '/dashboard');
                window.location.reload(0);
              }, 500);
              setOpen(false);
            }}
          >
            Try Beta UI
          </Button>
        </DialogActions>
      </Dialog>
      <Button
        style={{
          position: 'fixed',
          right: 0,
          bottom: 0,
          marginBottom: 15,
          marginRight: 10,
          padding: 5,
          zIndex: 1,
        }}
        variant={'contained'}
        color={'primary'}
        onClick={() => setOpen(true)}
      >
        Beta Test UI
      </Button>
    </div>
  );
}
