import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';

import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import ListHeader from '../../../../components/shared/ListHeader/ListHeader';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';
import SectionHeader from '../../../../components/shared/SectionHeader/SectionHeader';
import RepoItem from '../../../../components/core/RepoItem/RepoItem';
import Divider from '../../../../components/shared/Divider/Divider';

const Repos = () => {
  const [repos, setRepos] = useState(undefined);
  const [selectedRepo, setSelectedRepo] = useState(undefined);
  const [refresh, setRefresh] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const {enqueueSnackbar} = useSnackbar();

  useEffect(() => {
    axios.get('/api/public/repos').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.repos) {
        setRepos(data.repos);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [refresh]);

  const deleteRepo = () => {
    axios.delete(`/api/public/repos/delete/${selectedRepo}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
      setRefresh((prev) => ++prev);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const handleDeleteRepo = () => {
    deleteRepo();
    setSelectedRepo(null);
    setDialogOpen(false);
  };

  const DeleteDialog = () => (
    <Dialog
      open={dialogOpen}
      onClose={() => setDialogOpen(false)}
    >
      <DialogTitle>Are you sure you want to delete your repo?</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Are you sure you want to delete this repo, and all of the associated submissions?
          This action cannot be easily undone, if at all.
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setDialogOpen(false)} color="primary" variant={'contained'} autoFocus>
          Cancel
        </Button>
        <Button onClick={handleDeleteRepo} color="Secondary" variant={'contained'}>
          Yes delete my repo
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <StandardLayout>
      <DeleteDialog />
      <SectionHeader isPage title='Repos' />
      <Divider />
      <ListHeader sections={['Assignment Name', 'Status', 'Actions']} />
      {repos && repos.map((repo, index) => (
        <RepoItem
          key={`${repo.assignment_name}-${index}`}
          assignmentId={repo.assignment_id}
          assignmentName={repo.assignment_name}
          courseCode={repo.course_code}
          ready={repo.ready}
          repo_url={repo.repo_url}
          openDialog={(id) => {
            setDialogOpen(true);
            setSelectedRepo(id);
          }}
        />
      ))}
    </StandardLayout>
  );
};

export default Repos;
