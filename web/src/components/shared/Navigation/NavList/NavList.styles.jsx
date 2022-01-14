import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    paddingLeft: theme.spacing(2),
  },
  categoryHeader: {
    marginTop: `${theme.spacing(2)}px`,
    color: theme.palette.primary.main,
    letterSpacing: '3px',
  },
  categoryHeaderText: {
    fontSize: '12px',
  },
  item: {
    color: theme.palette.gray['200'],
    fontSize: '14px',
    '&:hover,&:focus': {
      backgroundColor: 'rgba(255, 255, 255, 0.08)',
    },
  },
  itemCategory: {
    backgroundColor: '#232f3e',
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
  },
  bottomPush: {
    paddingLeft: theme.spacing(2),
  },
  firebase: {
    fontSize: 24,
    color: theme.palette.white,
  },
  itemActiveItem: {
    color: '#4fc3f7',
  },
  itemPrimary: {
    fontSize: 'inherit',
  },
  itemIcon: {
    minWidth: 'auto',
    marginRight: theme.spacing(2),
  },
}));
