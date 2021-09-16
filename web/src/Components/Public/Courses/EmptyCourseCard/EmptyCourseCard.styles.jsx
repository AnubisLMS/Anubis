import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  emptyCourseCardContainer: {
    color: theme.palette.white,
    cursor: 'pointer',
    flexGrow: 1,
    minWidth: 275,
    maxWidth: 280,
    minHeight: 140,
    maxHeight: 150,
    borderColor: theme.palette.dark.blue['200'],
    border: '2px dashed',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '20px',
    borderRadius: '10px',
    '&:hover': {
      background: theme.palette.dark.blue['100'],
    },
  },
  joinText: {},
}));
