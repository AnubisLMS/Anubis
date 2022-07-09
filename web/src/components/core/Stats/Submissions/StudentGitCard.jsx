import React from 'react';

import makeStyles from '@mui/styles/makeStyles';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import GitHubIcon from '@mui/icons-material/GitHub';

const useStyles = makeStyles((theme) => ({
  title: {
    display: 'inline',
    margin: theme.spacing(1),
  },
}));

export default function StudentGitCard({submission}) {
  const classes = useStyles();

  if (!submission) {
    return null;
  }

  const {commit = '', repo = ''} = submission;
  const shortCommit = (commit ?? '').substr(0, 6);

  return (
    <Card className={classes.root}>
      <CardContent>
        <GitHubIcon color={'primary'} fontSize={'small'}/>
        <Typography variant={'h6'} className={classes.title}>
          Git / Github
        </Typography>
        <Typography color="textSecondary" gutterBottom>
          Repo: {repo}
        </Typography>
        <Typography color="textSecondary" gutterBottom>
          Commit: {shortCommit}
        </Typography>
      </CardContent>
      <CardActions>
        <Button
          size="small"
          color={'primary'}
          variant={'contained'}
          component={'a'}
          target={'_blank'}
          href={repo}
          startIcon={<GitHubIcon/>}
        >
          Go to repo at HEAD
        </Button>
        <Button
          size="small"
          color={'primary'}
          variant={'contained'}
          component={'a'}
          target={'_blank'}
          href={`${repo}/tree/${commit}`}
          startIcon={<GitHubIcon/>}
        >
          Go to repo at {shortCommit}
        </Button>
      </CardActions>
    </Card>
  );
}
