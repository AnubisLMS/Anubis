import React from 'react';
import makeStyles from '@mui/material/styles/makeStyles';
import TextField from '@mui/material/TextField';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import CardActions from '@mui/material/CardActions';
import Button from '@mui/material/Button';
import SaveIcon from '@mui/icons-material/Save';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
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
