import {makeStyles} from '@material-ui/core/styles';

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
}));
