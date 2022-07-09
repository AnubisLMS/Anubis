import {makeStyles} from '@mui/material/styles';

export const useStyles = makeStyles((theme) => ({
  green: {
    color: theme.palette.color.green,
  },
  red: {
    color: theme.palette.color.red,
  },
  deleteButton: {
    marginRight: theme.spacing(1),
  },
  actionsContainer: {
    display: 'flex',
  },
}));

