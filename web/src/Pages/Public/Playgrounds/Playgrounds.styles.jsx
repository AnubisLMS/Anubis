import {makeStyles} from '@material-ui/core/styles';
import green from '@material-ui/core/colors/green';

export const useStyles = makeStyles((theme) => ({
  imageTagContainer: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    padding: theme.spacing(2),
  },
  actionContainer: {
    padding: theme.spacing(2),
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    display: 'flex',
    alignItems: 'center',
  },
  divider: {
    width: '100%',
    borderTop: `1px solid ${theme.palette.dark.blue['200']}`,
    marginTop: theme.spacing(2),
    height: '1px',
  },
  paper: {
    width: '100%',
    maxWidth: '700px',
    padding: theme.spacing(2),
  },
  imageContainer: {
    marginTop: theme.spacing(2),
  },
  image: {
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'space-between',
    'paddingRight': theme.spacing(4),
    'paddingLeft': theme.spacing(4),
    'paddingTop': theme.spacing(2),
    'paddingBottom': theme.spacing(2),
    'border': `1px solid ${theme.palette.dark.blue['200']}`,
    'borderRadius': '2px',
    'cursor': 'pointer',
    '&:hover': {
      border: `1px solid ${theme.palette.primary.main}`,
    },
  },
  opFull: {
    opacity: '1',
  },
  opLess: {
    opacity: '.5',
  },
  tagListContainer: {
    marginTop: theme.spacing(1),
  },
  selectedImage: {
    border: `1px solid ${theme.palette.primary.main}`,
  },
  imageHeader: {
    display: 'flex',
    alignItems: 'center',
  },
  imageLabel: {
    marginLeft: theme.spacing(1),
    paddingBottom: theme.spacing(.5),
    paddingTop: theme.spacing(.5),
    paddingRight: theme.spacing(1),
    paddingLeft: theme.spacing(1),
    backgroundColor: theme.palette.primary.main,
    borderRadius: '20px',
  },
  imageDescription: {
    marginTop: -theme.spacing(1),
  },
  button: {
    paddingTop: theme.spacing(1),
    paddingBottom: theme.spacing(1),
    borderRadius: '2px',
    width: '100%',
  },
  buttonProgress: {
    color: green[500],
    position: 'absolute',
    top: '50%',
    left: '50%',
    marginTop: -12,
    marginLeft: -12,
  },
  wrapper: {
    position: 'relative',
  },
  buttonSuccess: {
    'backgroundColor': green[500],
    '&:hover': {
      backgroundColor: green[700],
    },
  },
  sessionState: {
    marginLeft: theme.spacing(2),
    opacity: '.8',
  },
  left: {
    marginLeft: 'auto',
  },
  buttonWrapper: {
    display: 'flex',
    flexDirection: 'row',
  },
  icon: {
    marginLeft: theme.spacing(1),
    marginRight: theme.spacing(1),
  },
  tooltip: {
    fontSize: '16px',
  },
}));
