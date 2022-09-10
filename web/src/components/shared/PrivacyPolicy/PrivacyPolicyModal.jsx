import React from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import Button from '@mui/material/Button';
import PrivacyPolicy from './PrivacyPolicy';
import VisibilityIcon from '@mui/icons-material/Visibility';

export default function PrivacyPolicyModal() {
  const [open, setOpen] = React.useState(false);

  return (
    <React.Fragment>
      <Button
        variant={'contained'}
        color={'primary'}
        onClick={() => setOpen(true)}
        startIcon={<VisibilityIcon/>}
      >
        View
      </Button>
      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>
          Privacy Policy
        </DialogTitle>
        <DialogContent>
          <PrivacyPolicy/>
        </DialogContent>
        <DialogActions>
          <Button variant={'contained'} onClick={() => setOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}
