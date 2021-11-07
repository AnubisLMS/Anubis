import {makeStyles} from '@material-ui/core';

export const useStyles = makeStyles((theme) => ({
  inline: {
    display: 'inline',
  },
  divider: {
    width: '100%',
    borderTop: `1px solid ${theme.palette.dark.blue['200']}`,
    marginTop: theme.spacing(2),
    height: '1px',
  },
}));
