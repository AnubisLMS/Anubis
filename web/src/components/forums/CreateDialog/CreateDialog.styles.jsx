import makeStyles from '@mui/styles/makeStyles';

export const useStyles = makeStyles((theme) => ({
  root: {
    width: '800px',
  },
  switchContainer: {
    display: 'flex',
    alignItems: 'center',
    margin: theme.spacing(0),
    padding: theme.spacing(0),
  },
  buttonIcon: {
    color: theme.palette.primary.main,
  },
  submit: {
    borderTopLeftRadius: 0,
    borderTopRightRadius: 0,
  },
  titleContainer: {
    backgroundColor: `${theme.palette.primary.main}80`,
    padding: theme.spacing(1.5),
    fontSize: '1rem',
  },
  inputTitle: {
    padding: theme.spacing(1.5, 1, 1.5, 1),
    fontSize: '2.25rem',
  },
}));

