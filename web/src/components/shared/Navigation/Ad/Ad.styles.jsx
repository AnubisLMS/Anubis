import makeStyles from '@mui/styles/makeStyles';

export const useStyles = makeStyles((theme) => ({
  root: {
    borderRadius: theme.spacing(1),
    width: '100%',
    overflow: 'inherit',
  },
  actionArea: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: `${theme.spacing(5)} ${theme.spacing(2)} ${theme.spacing(2)}`,
    width: '100%',
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
    zIndex: 3,
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
    fontSize: '18px',
    textAlign: 'center',
    padding: theme.spacing(0, 1),
  },
  githubButton: {
    width: '100%',
    marginTop: theme.spacing(2),
    backgroundColor: theme.palette.primary.main,
    borderRadius: '2px',
  },
}));
