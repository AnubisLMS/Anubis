import React from 'react';
import {useHistory} from 'react-router-dom';

import GitHubIcon from '@material-ui/icons/GitHub';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Box from '@material-ui/core/Box';

import {useStyles} from './RepoItem.styles';
import Item from '../../Shared/Item/Item';

const RepoItem = ({
  assignmentName,
  courseCode,
  githubUsername,
  ready,
  repo_url,
  openDialog,
}) => {
  const history = useHistory();
  const classes = useStyles();

  return (
    <Item
      showStatus={false}
      title={assignmentName}
      subTitle={courseCode}
      titleIcon={<GitHubIcon />}
      link={repo_url}
    >
      <Typography>{githubUsername}</Typography>
      <Typography>{ready ? 'Ready' : 'Processing'}</Typography>
      <Box className={classes.actionsContainer}>
        <Button
          className={classes.deleteButton}
          onClick={openDialog}
        >
          Delete Repo
        </Button>
        <Button
          onClick={() => history.push(repo_url)}
        >
          View Repo
        </Button>
      </Box>

    </Item>
  );
};

export default RepoItem;
