import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    display: 'flex',
    padding: theme.spacing(2),
    alignItems: 'center',
    justifyContent: 'center',
  },
  paginate: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1),
  },
  active: {
    backgroundColor: theme.palette.dark.blue['200'],
  },
  page: {
    border: `1px solid ${theme.palette.dark.blue['200']}`,
  },
}));
