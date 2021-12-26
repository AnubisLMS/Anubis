import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';

import StandardLayout from '../../../Components/Shared/Layouts/StandardLayout';
import ListHeader from '../../../Components/Shared/ListHeader/ListHeader';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import SectionHeader from '../../../Components/Shared/SectionHeader/SectionHeader';
import RepoItem from '../../../Components/Public/RepoItem/RepoItem';
import Divider from '../../../Components/Shared/Divider/Divider';

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
        console.log(data.repos);
        setRepos(data.repos);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [refresh]);

  const deleteRepo = () => {
    axios.delete(`/api/public/repos/delete/${selectedRepo.assignment_id}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
      setRefresh((prev) => ++prev);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const handleDeleteRepo = () => {
    deleteRepo();
    selectedRepo(null);
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
      <ListHeader sections={['Assignment Name', 'Github Username', 'Status', 'Actions']} />
      {repos && repos.map((repo, index) => (
        <RepoItem
          key={`${repo.assignment_name}-${index}`}
          assignmentName={repo.assignment_name}
          courseCode={repo.course_code}
          githubUsername={repo.github_username}
          ready={repo.ready}
          openDialog={() => setDialogOpen(true)}
        />
      ))}
    </StandardLayout>
  );
};

export default Repos;
