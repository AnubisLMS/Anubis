import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  avatar: {
    zIndex: 999,
    marginLeft: theme.spacing(2),
    width: '35px',
    height: '35px',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.palette.primary.main,
    borderRadius: '100%',
    cursor: 'pointer',
    '&:hover': {
      opacity: 0.8,
    },
  },
  clickableContainer: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
  },
  expandIcon: {
    marginLeft: theme.spacing(1),
    opacity: .3,
  },
  profileActions: {
    paddingTop: theme.spacing(2),
    width: '250px',
    borderRadius: theme.spacing(.5),
    backgroundColor: theme.palette.dark.blue['200'],
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    position: 'absolute',
    top: theme.spacing(7),
    right: 0,
  },
  contextTitle: {
    padding: `${theme.spacing(0)}px ${theme.spacing(6)}px ${theme.spacing(1)}px ${theme.spacing(2)}px`,
    color: theme.palette.primary.main,
    letterSpacing: '2px',
    fontSize: '12px',
  },
  profileAction: {
    padding: `${theme.spacing(0)}px ${theme.spacing(6)}px ${theme.spacing(1)}px ${theme.spacing(2)}px`,
    cursor: 'pointer',
    color: theme.palette.gray['200'],
    display: 'flex',
    flexDirection: 'row',
    width: '100%',
    '&:hover': {
      color: theme.palette.white,
    },
  },
  profileActionText: {
    fontSize: '16px',
  },
  selectedCourse: {
    cursor: 'pointer',
    padding: `${theme.spacing(1)}px ${theme.spacing(6)}px ${theme.spacing(1)}px ${theme.spacing(3)}px`,
    backgroundColor: '#2A3039',
    marginBottom: theme.spacing(1),
  },
  course: {
    cursor: 'pointer',
    '&:hover': {
      backgroundColor: '#2A3039',
    },
    color: theme.palette.gray['200'],
    padding: `${theme.spacing(1)}px ${theme.spacing(6)}px ${theme.spacing(1)}px ${theme.spacing(3)}px`,
    marginBottom: theme.spacing(1),
  },
}));
