import {makeStyles} from '@material-ui/core';

export const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
  },
  heading: {
    padding: theme.spacing(2),
    display: 'flex',
  },
  wrapper: {
    margin: theme.spacing(1),
    position: 'relative',
  },
  buttonSuccess: {
    'backgroundColor': theme.palette.color.green,
    '&:hover': {
      backgroundColor: theme.palette.color.green,
    },
  },
  fabProgress: {
    color: theme.palette.color.green,
    position: 'absolute',
    top: -6,
    left: -6,
    zIndex: 1,
  },
  buttonProgress: {
    color: theme.palette.color.green,
    position: 'absolute',
    top: '50%',
    left: '50%',
    marginTop: -12,
    marginLeft: -12,
  },
}));
