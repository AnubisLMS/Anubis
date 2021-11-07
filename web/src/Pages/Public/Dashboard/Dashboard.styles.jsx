import makeStyles from '@material-ui/core/styles/makeStyles';

export const useStyles = makeStyles((theme) => ({
  divider: {
    width: '100%',
    borderTop: `1px solid ${theme.palette.dark.blue['200']}`,
    marginTop: theme.spacing(2),
    height: '1px',
  },
}));
