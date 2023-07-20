import makeStyles from '@mui/styles/makeStyles';

export const useStyles = makeStyles((theme) => ({
  publisherContainer: {
    width: '100%',
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    borderBottomLeftRadius: '10px',
    borderBottomRightRadius: '10px',
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
    width: '100%',
  },
  titleContainer: {
    backgroundColor: `${theme.palette.primary.main}80`,
    padding: theme.spacing(1.5),
    fontSize: '1rem',
    width: '100%',
  },
  inputTitle: {
    padding: theme.spacing(1.5, 1, 1.5, 1),
    fontSize: '2.25rem',
  },
}));

