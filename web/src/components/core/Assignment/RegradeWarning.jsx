import React from 'react';

import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import yellow from '@mui/material/colors/yellow';


export default function RegradeWarning({warningOpen, setWarningOpen, regradeAssignment}) {
  const RegradeButton = ({title, params = {}}) => (
    <Button
      onClick={() => {
        setWarningOpen(false);
        regradeAssignment(params);
      }}
      color={'secondary'}
      variant={'contained'}
      size={'small'}
    >
      {title}
    </Button>
  );

  return (
    <Dialog
      open={warningOpen}
      onClose={() => setWarningOpen(false)}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <DialogTitle id="alert-dialog-title">
        Are you sure you want to proceed?
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="alert-dialog-description">
          A regrade can take a very long time to complete. Please verify that
          you would like to proceed with the regrade.
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button
          color="primary"
          onClick={() => setWarningOpen(false)}
          variant={'contained'}
          size={'small'}
          autoFocus
        >
          Cancel
        </Button>
        <RegradeButton
          title={'Regrade all'}
        />
        <RegradeButton
          title={'Regrade latest only'}
          params={{latest_only: true}}
        />
        <RegradeButton
          title={'Regrade last 6 hours'}
          params={{hours: '6'}}
        />
        <RegradeButton
          title={'Regrade last hour'}
          params={{hours: '1'}}
        />
      </DialogActions>
    </Dialog>
  );
}
