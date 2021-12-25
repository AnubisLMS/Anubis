import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: `${theme.spacing(5)}px ${theme.spacing(2)}px ${theme.spacing(2)}px`,
    borderRadius: `${theme.spacing(1)}px`,
    width: '90%',
    backgroundColor: theme.palette.dark.blue['200'],
  },
  iconContainer: {
    width: '45px',
    height: '45px',
    position: 'absolute',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '100%',
    backgroundColor: theme.palette.color.blue,
    top: '-23px',
  },
  iconInnerCircle: {
    backgroundColor: theme.palette.primary.main,
    width: '35px',
    height: '35px',
    borderRadius: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  adTitle: {
    fontSize: '14px',
  },
  githubButton: {
    width: '100%',
    marginTop: theme.spacing(2),
    backgroundColor: theme.palette.primary.main,
    borderRadius: '2px',
  },
}));
