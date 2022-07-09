import {makeStyles} from '@mui/material/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    marginTop: theme.spacing(4),
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  pageTitle: {
    fontSize: '26px',
    fontWeight: 600,
  },
  title: {
    fontSize: '20px',
    fontWeight: 500,
  },
  button: {
    color: theme.palette.color.blue,
    '&:hover': {
      backgroundColor: 'transparent',
      color: theme.palette.primary.main,
    },
  },
}));
