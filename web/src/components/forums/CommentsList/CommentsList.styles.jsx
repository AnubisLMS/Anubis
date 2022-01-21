import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    borderLeft: `1px solid ${theme.palette.dark.blue['200']}`,
    paddingLeft: theme.spacing(1.5),
    overflow: 'scroll',
  },
  replies: {
    display: 'flex',
    flexDirection: 'column',
    marginLeft: theme.spacing(2),
    paddingLeft: theme.spacing(2),
    borderLeft: `1px solid ${theme.palette.dark.blue['200']}`,
  },
}));
