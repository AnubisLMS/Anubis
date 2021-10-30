import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(3),
    borderRadius: theme.spacing(1),
    backgroundColor: theme.palette.dark.blue['200'],
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    height: '60px',
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
  },
  circleIcon: {
    width: '20px',
    height: '20px',
  },
  iconWrapper: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '14px',
  },
  name: {
    fontSize: '16px',
    marginLeft: theme.spacing(1),
  },
  testStatus: {
    alignSelf: 'flex-end',
    marginLeft: theme.spacing(1),
  },
  success: {
    color: theme.palette.color.green,
  },
  error: {
    color: theme.palette.color.red,
  },
  expand: {
    fontSize: '14px',
  },
}));
