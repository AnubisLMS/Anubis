import {makeStyles} from '@mui/material/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    cursor: 'pointer',
    height: '70px',
    width: '100%',
    padding: theme.spacing(2),
    borderRadius: theme.spacing(.5),
    marginTop: theme.spacing(2),
    border: `1px dashed ${theme.palette.dark.blue['200']}`,
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    '&:hover': {
      border: `1px dashed #3A3F47`,
      backgroundColor: theme.palette.dark.blue['100'],
    },
  },
  text: {
    marginLeft: theme.spacing(2),
  },
}));

