import React, {useState} from 'react';
import makeStyles from '@mui/styles/makeStyles';
import TextField from '@mui/material/TextField';
import Grid from '@mui/material/Grid';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';
import axios from 'axios';

const useStyles = makeStyles((theme) => ({
  root: {
    '& > *': {
      margin: theme.spacing(1),
    },
    'flexGrow': 1,
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.colors.orange,
    width: 200,
  },
  margin: {
    margin: theme.spacing(1),
  },
  extendedIcon: {
    marginRight: theme.spacing(1),
  },
}));

export default function GetGithubUsername() {
  const classes = useStyles();
  const [github_username, setUsername] = useState('');
  const [chip, setChip] = useState({
    label: 'test',
    hidden: true,
    color: 'primary',
  });

  const uploadUsername = () => {
    axios.get('/api/public/set-github-username', {
      params: {github_username},
    }).then((response) => {
      if (response.data.success) {
        setTimeout(() => window.location = '/courses', 2000);
        setChip({
          label: `Github username is set to ${response.data.data}`,
          hidden: false, color: 'primary',
        });
      } else {
        setChip({
          label: response.data.error,
          hidden: false, color: 'error',
        });
      }
    }).catch((error) => {
      if (error.response.status === 401) {
        window.location = '/api/public/login';
      }
      setChip({
        label: 'Unable to reach API',
        hidden: false, color: 'error',
      });
    });
  };

  return (
    <Grid container justifyContent="center" alignContent={'center'} direction={'column'} spacing={1}>

      {!chip.hidden ?
        <Chip
          label={<Typography variant={'h6'}>{chip.label}</Typography>}
          onDelete={() => {
            setChip({label: '', hidden: true, color: 'primary'});
          }}
          color={chip.color}
          hidden={chip.hidden}/> :
        null}

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Grid container justifyContent="center" alignContent={'center'} direction={'column'} spacing={1}>
              <Grid item xs={12}>
                <Typography variant={'h6'}>
                  Please enter your Github Username
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Username"
                  name={'github_username'}
                  variant="outlined"
                  value={github_username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </Grid>
            </Grid>
          </CardContent>
          <CardActions>
            <Button variant="contained" size="medium" color="primary"
              className={classes.margin} onClick={uploadUsername}>
              Submit
            </Button>
          </CardActions>
        </Card>
      </Grid>

    </Grid>
  );
}
