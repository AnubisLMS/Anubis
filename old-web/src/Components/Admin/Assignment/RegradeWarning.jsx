import React from 'react';

import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import Button from '@material-ui/core/Button';
import yellow from '@material-ui/core/colors/yellow';


export default function RegradeWarning({warningOpen, setWarningOpen, regradeAssignment}) {
  const RegradeButton = ({title, params = {}}) => (
    <Button
      onClick={() => {
        setWarningOpen(false);
        regradeAssignment(params);
      }}
      style={{backgroundColor: yellow[500]}}
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
          title={'Regrade Reaped'}
          params={{reaped: 1}}
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
