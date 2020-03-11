import React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import {makeStyles} from "@material-ui/core/styles";
import {green} from "@material-ui/core/colors";

const useStyles = makeStyles(theme => ({
  paper: {
    maxWidth: 936,
    margin: theme.spacing(2),
    padding: theme.spacing(2),
    overflow: 'hidden',
  },
  searchBar: {
    borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
  },
  searchInput: {
    fontSize: theme.typography.fontSize,
  },
  title: {
    fontSize: 14,
  },
  block: {
    display: 'block',
  },
  addUser: {
    marginRight: theme.spacing(1),
  },
  contentWrapper: {
    margin: '40px 16px',
  },
  card: {
    minWidth: 275,
  },
  list: {
    width: '100%',
  },
  dialog: {
    margin: theme.spacing(2),
    padding: theme.spacing(2)
  },
  closeButton: {
    position: 'absolute',
    right: theme.spacing(1),
    top: theme.spacing(1),
    color: theme.palette.grey[500],
  },
  progress: {
    padding: theme.spacing(1)
  },
  fabProgress: {
    color: green[500],
    position: 'absolute',
    top: -6,
    left: -6,
    zIndex: 1,
  },
  buttonProgress: {
    color: green[500],
    position: 'absolute',
    top: '50%',
    left: '50%',
    marginTop: -12,
    marginLeft: -12,
  },
  wrapper: {
    margin: theme.spacing(1),
    position: 'relative',
  },
}));

export default function Auth(props) {
  const classes = useStyles();
  const {
    open,
    onClose,
    verify,
    commit,
    setNetid
  } = props;

  return (
    <Dialog open={open} onClose={onClose} className={classes.dialog}>
      <DialogTitle>
        Verification
      </DialogTitle>
      <DialogContent>
        <DialogContentText>
          Please verify your netid to see the submission data for <br/>{commit}
        </DialogContentText>
        <TextField
          required
          autoFocus
          fullWidth
          margin={'dense'}
          variant={'outlined'}
          label={'netid'}
          onChange={e => setNetid(e.target.value)}
          onKeyPress={e => e.key === 'Enter' ? verify() : null}
        />
      </DialogContent>
      <DialogActions>
        <Button variant="contained" color="primary" onClick={verify}>
          Verify
        </Button>
      </DialogActions>
    </Dialog>
  );
}