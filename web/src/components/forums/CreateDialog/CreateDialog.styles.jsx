import makeStyles from '@mui/styles/makeStyles';

export const useStyles = makeStyles((theme) => ({
  root: {
    width: '800px',
  },
  switchContainer: {
    display: 'flex',
    alignItems: 'center',
  },
  editorContainer: {
    display: 'block',
    height: '400px',
    margin: theme.spacing(10),
    padding: theme.spacing(1),
  },
  buttonIcon: {
    color: theme.palette.primary.main,
  },
  toolbarContainer: {
    borderColor: theme.palette.white,
    borderTop: theme.spacing(0.1) + ' solid',
    borderBottom: theme.spacing(0.1) + ' solid',
  },
  submit: {
    borderTopLeftRadius: 0,
    borderTopRightRadius: 0,
  },
  titleContainer: {
    backgroundColor: `${theme.palette.primary.main}80`,
    padding: theme.spacing(1.5),
  },
  inputTitle: {
    padding: theme.spacing(1.5, 1, 1.5, 1),
    fontSize: '1rem',
    borderBottom: '0', // Not working
  },
}));

