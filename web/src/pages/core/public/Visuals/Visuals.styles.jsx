import {makeStyles} from '@mui/material/styles';

export const useStyles = makeStyles((theme) => ({
  usage: {
    height: 0,
    paddingTop: '83.33%', // 16:9
  },
  title: {
    padding: theme.spacing(1, 2),
    fontSize: 16,
  },
  button: {
    margin: theme.spacing(2, 1),
  },
  autocomplete: {
    paddingBottom: theme.spacing(1),
    paddingLeft: theme.spacing(1),
    paddingRight: theme.spacing(1),
  },
  paper: {
    flex: 1,
    padding: theme.spacing(1),
  },
}));
