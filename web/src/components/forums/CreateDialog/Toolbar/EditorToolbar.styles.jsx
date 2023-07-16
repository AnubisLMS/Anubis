import makeStyles from '@mui/styles/makeStyles';
export const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'flex-start',
    alignItems: 'center',
    padding: theme.spacing(0),
    margin: theme.spacing(0.5, 0.25),
  },
  p: {
    margin: theme.spacing(0),
  },
  IconLogo: {
    translate: 'transform(-50%, -50%)',
    padding: theme.spacing(0.1),
  },
}));
