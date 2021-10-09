import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  submissionContainer: {
    color: theme.palette.white,
    flexGrow: 1,
    width: '100%',
    height: '500px',
    backgroundColor: 'transparent',
    display: 'flex',
    flexDirection: 'column',
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    borderRadius: `${theme.spacing(1.4)}px`,
  },
  headerContainer: {
    width: '100%',
    display: 'flex',
    flexDirection: 'row',
    backgroundColor: theme.palette.dark.blue['200'],
    backgroundColor: '#21262D',
    border: '1px solid white',
    borderColor: 'transparent',
    borderRadius: `${theme.spacing(1.25)}px ${theme.spacing(1.25)}px 0px 0px`,
    padding: `${theme.spacing(1.4)}px`,
  },
  failedContainer: {
    color: theme.palette.color.red,
    flexGrow: 1,
    fontSize: '18px',
    backgroundColor: '#21262D',
    paddingLeft: `${theme.spacing(1.4)}px`,
    paddingTop: `${theme.spacing(0.6)}px`,
  },
  statsContainer: {
    color: theme.palette.white,
    fontSize: '13px',
    flexGrow: 1,
    backgroundColor: '#21262D',
    paddingLeft: `${theme.spacing(1.4)}px`,
  },
}));
