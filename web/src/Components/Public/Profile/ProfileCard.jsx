import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import TextField from '@material-ui/core/TextField';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';

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


export default function ProfileCard({user, github_username, set_github_username}) {
  const classes = useStyles();

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
          disabled
          label="Github Username"
          className={classes.textField}
          onChange={(e) => set_github_username(e.target.value)}
          value={github_username}
          variant="outlined"
        />
      </CardContent>
      {/* <CardActions>*/}
      {/*  <Button*/}
      {/*    variant="contained"*/}
      {/*    color="primary"*/}
      {/*    className={classes.button}*/}
      {/*    startIcon={<SaveIcon/>}*/}
      {/*    onClick={() => axios.get(`/api/public/set-github-username?github_username=${github_username}`)}*/}
      {/*  >*/}
      {/*    Save*/}
      {/*  </Button>*/}
      {/* </CardActions>*/}
    </Card>
  );
}
