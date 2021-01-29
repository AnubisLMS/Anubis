import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import TextField from '@material-ui/core/TextField';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import CardActions from '@material-ui/core/CardActions';
import Button from '@material-ui/core/Button';
import SaveIcon from '@material-ui/icons/Save';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import {useSnackbar} from 'notistack';
import axios from 'axios';

const useStyles = makeStyles((theme) => ({
  card: {
    minWidth: 300,
  },
  cardContent: {
    flexDirection: 'column',
    display: 'flex',
  },
  textField: {
    margin: theme.spacing(1),
  },
}));

const saveGithubUsername = (github_username, enqueueSnackbar) => () => {
  axios.post(`/api/public/auth/set-github-username`, {github_username}).then((response) => {
    standardStatusHandler(response, enqueueSnackbar);
  }).catch(standardErrorHandler(enqueueSnackbar));
};


export default function ProfileCard({user, github_username, set_github_username}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  return (
    <Card variant="outlined" className={classes.card}>
      <CardContent className={classes.cardContent}>
        <Typography className={classes.title} color="textSecondary" gutterBottom>
          Anubis profile
        </Typography>
        <TextField
          disabled
          label="Name"
          className={classes.textField}
          value={user.name.trim()}
          variant="outlined"
        />
        <TextField
          disabled
          label="Netid"
          className={classes.textField}
          value={user.netid.trim()}
          variant="outlined"
        />
        <TextField
          label="Github Username"
          className={classes.textField}
          onChange={(e) => set_github_username(e.target.value)}
          value={github_username}
          variant="outlined"
        />
      </CardContent>
      <CardActions>
        <Button
          variant="contained"
          color="primary"
          className={classes.button}
          startIcon={<SaveIcon/>}
          onClick={saveGithubUsername(github_username, enqueueSnackbar)}
        >
          Save
        </Button>
      </CardActions>
    </Card>
  );
}
