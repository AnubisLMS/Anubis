import makeStyles from '@mui/styles/makeStyles';

export const useStyles = makeStyles((theme) => ({
  root: {
    paddingLeft: theme.spacing(2),
  },
  categoryHeader: {
    marginTop: theme.spacing(2),
    color: theme.palette.primary.main,
    letterSpacing: '3px',
  },
  categoryHeaderText: {
    fontSize: '12px',
  },
  item: {
    color: theme.palette.color.gray,
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
    marginBottom: theme.spacing(2),
  },
  firebase: {
    fontSize: 24,
    color: theme.palette.color.white,
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
