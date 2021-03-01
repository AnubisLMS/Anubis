import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';

import GitHubIcon from '@material-ui/icons/GitHub';

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

  const {commit='', repo=''} = submission;
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
