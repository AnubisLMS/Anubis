import React, {useState} from 'react';
import makeStyles from '@mui/styles/makeStyles';
import Button from '@mui/material/Button';
import axios from 'axios';
import Box from '@mui/material/Box';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import DeleteForever from '@mui/icons-material/DeleteForever';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import useMediaQuery from '@mui/material/useMediaQuery';
import {useTheme} from '@mui/material/styles';
import {useSnackbar} from 'notistack';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';

const useStyles = makeStyles((theme) => ({
  root: {
    '& > *': {
      margin: theme.spacing(1),
    },
    'flexGrow': 1,
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.colors.orange,
    width: 200,
  },
  margin: {
    margin: theme.spacing(1),
  },
  extendedIcon: {
    marginRight: theme.spacing(1),
  },
}));

// Generate the actual button and the box, private
function generateDeletePvcComponent(deleteThePvc, netid = ``) {
  const [confirm, setConfirm] = useState(false);
  const [open, setOpen] = useState(false);
  const {enqueueSnackbar} = useSnackbar();
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('md'));

  const handleOpen = () => {
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
  };

  return (
    <Box>
      <Dialog
        fullScreen={fullScreen}
        open={open}
        onClose={handleClose}
        aria-labelledby="responsive-dialog-title"
      >
        <DialogTitle id="responsive-dialog-title">
          Are you sure you want to continue?
        </DialogTitle>
        <DialogContent>
          {netid === `` ? (
            <DialogContentText>
              You are about to delete your Anubis Cloud IDE volume. This will delete
              your home directory, and any work that resides there. If you have a IDE
              open, the delete will occur after your IDE is stopped. This action cannot
              be undone. Please confirm to continue.
            </DialogContentText>
          ) : (
            <DialogContentText>
              You are about to delete the Anubis Cloud IDE volume for user with NET ID: {`${netid}`}. This will delete
              their home directory, and any work that resides there. If they have a IDE
              open, the delete will occur after their IDE is stopped. This action cannot
              be undone. Please confirm to continue.
            </DialogContentText>
          )}
          <FormControlLabel
            control={
              <Switch
                checked={confirm}
                color={'error'}
                onChange={(_, v) => setConfirm(v)}
              />
            }
            labelPlacement={'end'}
            label={<i>Yes I confirm I would like to delete my Cloud IDE Volume</i>}
          />
        </DialogContent>
        <DialogActions>
          <Button
            autoFocus
            onClick={handleClose}
            color={'primary'}
            variant={'contained'}
          >
            Cancel
          </Button>
          <Button
            startIcon={<DeleteForever/>}
            disabled={!confirm}
            onClick={() => {
              handleClose();
              deleteThePvc();
            }}
            color={'error'}
            variant={'contained'}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
      <Box sx={{m: 1}}>
        <Button
          color={'error'}
          variant={'contained'}
          startIcon={<DeleteForever/>}
          onClick={handleOpen}
        >
          Delete
        </Button>
      </Box>
    </Box>
  );
}

export default function DeletePvc() {
  const deleteThePvc = () => {
    axios.delete(`/api/public/profile/pvc`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  return (generateDeletePvcComponent(deleteThePvc));
}

export function SuperDeletePvc({id, netid}) {
  const deleteThePvc = () => {
    axios.delete(`/api/super/students/pvc/${id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  return (generateDeletePvcComponent(deleteThePvc, netid));
}
