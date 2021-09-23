import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  item: {
    color: theme.palette.gray['200'],
    borderRadius: '4px 0 0 4px',
    '&:hover,&:focus': {
      backgroundColor: theme.palette.dark.blue['200'],
    },
  },
  itemActiveItem: {
    color: theme.palette.white,
    backgroundColor: theme.palette.dark.blue['200'],
  },
  itemPrimary: {
    fontSize: 'inherit',
  },
  itemIcon: {
    color: theme.palette.gray['200'],
    minWidth: 'auto',
    marginRight: theme.spacing(2),
  },
  itemActiveIcon: {
    color: theme.palette.white,
  },
}));
