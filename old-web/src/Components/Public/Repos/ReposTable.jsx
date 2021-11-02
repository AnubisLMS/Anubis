import React, {useState} from 'react';

import {DataGrid} from '@material-ui/data-grid';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

import IconButton from '@material-ui/core/IconButton';
import GitHubIcon from '@material-ui/icons/GitHub';
import DeleteForeverIcon from '@material-ui/icons/DeleteForever';
import axios from 'axios';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import {useSnackbar} from 'notistack';

const useStyles = makeStyles((theme) => ({
  paper: {
    height: 700,
    padding: theme.spacing(1),
  },
}));


const deleteRepo = (repoSelected, setReset, enqueueSnackbar) => {
  const {assignment_id} = repoSelected;

  axios.delete(`/api/public/repos/delete/${assignment_id}`).then((response) => {
    standardStatusHandler(response, enqueueSnackbar);
    setReset((prev) => ++prev);
  }).catch(standardErrorHandler(enqueueSnackbar));
};

const useColumns = ({setDeleteOpen, setRepoSelected}) => ([
  {field: 'course_code', headerName: 'Course', width: 150},
  {field: 'assignment_name', headerName: 'Assignment Name', width: 200},
  {field: 'github_username', headerName: 'Github Username', width: 200},
  {
    field: 'repo_url', headerName: 'Repo', width: 100, renderCell: ({row}) => (
      <IconButton
        color={'primary'}
        component={'a'}
        target={'_blank'}
        rel={'noreferrer'}
        href={row.repo_url}
      >
        <GitHubIcon/>
      </IconButton>
    ),
  },
  {
    field: 'delete', headerName: 'Delete', width: 100, renderCell: ({row}) => (
      <IconButton
        color={'secondary'}
        onClick={() => {
          setDeleteOpen(true);
          setRepoSelected({...row});
        }}
      >
        <DeleteForeverIcon/>
      </IconButton>
    ),
  },
]);

export default function ReposTable({rows, setReset}) {
  const classes = useStyles();
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [repoSelected, setRepoSelected] = useState(null);
  const {enqueueSnackbar} = useSnackbar();

  const columns = useColumns({
    deleteOpen, setDeleteOpen,
    repoSelected, setRepoSelected,
  });

  return (
    <div>
      <Dialog
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
      >
        <DialogTitle>Are you sure you want to delete your repo?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this repo, and all of the associated submissions?
            This action cannot be easily undone, if at all.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteOpen(false)} color="primary" variant={'contained'} autoFocus>
            Cancel
          </Button>
          <Button onClick={() => {
            deleteRepo(repoSelected, setReset, enqueueSnackbar);
            setRepoSelected(null);
            setDeleteOpen(false);
          }} color="Secondary" variant={'contained'}>
            Yes delete my repo
          </Button>
        </DialogActions>
      </Dialog>
      <Paper className={classes.paper}>
        <DataGrid columns={columns} rows={rows}/>
      </Paper>
    </div>
  );
}
