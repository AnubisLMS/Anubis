import {makeStyles} from '@material-ui/core';

export const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    position: 'relative',
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
  submissionContentContainer: {
    width: '100%',
    marginTop: theme.spacing(2),
  },
  expandedContainer: {
    zIndex: 599,
    position: 'absolute',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
    height: '100%',
  },
  headerContainer: {
    width: '100%',
  },
  backDrop: {
    zIndex: 500,
    position: 'absolute',
    top: 0,
    left: 0,
    height: '100%',
    width: '100%',
    opacity: '7%',
    backgroundColor: '#C4C4C4',
  },
  blur: {
    filter: 'blur(3px)',
  },
}));
