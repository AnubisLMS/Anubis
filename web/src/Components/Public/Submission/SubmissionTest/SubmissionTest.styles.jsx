import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  submissionTestMain: {
    padding: theme.spacing(2),
    borderRadius: '10px',
    background: theme.palette.dark.blue['200'],
    height: '79px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    display: 'flex',
    flexDirection: 'row',
  },
  circleIcon: {
    width: '20px',
    height: '20px',
  },
  iconWrapper: {
    marginTop: '6px',
    fontSize: '14px',
  },
  name: {
    marginLeft: '17px',
    fontSize: '20px',
  },
  testStatus: {
    marginLeft: '9px',
    paddingTop: '5px',
  },
  success: {
    color: theme.palette.color.green,
  },
  error: {
    color: theme.palette.color.red,
  },
  expand: {
    marginRight: '12px',
  },
}));
