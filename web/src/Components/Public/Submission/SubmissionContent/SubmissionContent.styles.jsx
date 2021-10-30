import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  submissionContainer: {
    color: theme.palette.white,
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    border: `2px solid ${theme.palette.dark.blue['200']}`,
    borderRadius: `${theme.spacing(1)}px`,
  },
  headerContainer: {
    width: '100%',
    display: 'flex',
    flexDirection: 'row',
    backgroundColor: theme.palette.dark.blue['200'],
    borderBottom: `1px solid ${theme.palette.dark.blue['200']}`,
    borderRadius: `${theme.spacing(1)}px ${theme.spacing(1)}px 0px 0px`,
    alignItems: 'center',
    padding: theme.spacing(2),
  },
  statusContainer: {
    display: 'flex',
    flexDirection: 'column',
    marginLeft: theme.spacing(2),
  },
  statusText: {
    fontSize: '16px',
    fontWeight: 600,
    color: theme.palette.white,
  },
  statusDescriptionText: {
    fontSize: '14px',
    opacity: '.8',
  },
  testListContainer: {
    padding: theme.spacing(2),
    '& > *': {
      marginTop: theme.spacing(2),
    },
  },
}));
