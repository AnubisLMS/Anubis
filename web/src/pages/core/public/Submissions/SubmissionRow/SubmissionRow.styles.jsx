import {makeStyles} from '@material-ui/core/styles';

export const useAnimations = () => {
  return {
    nameContainer: {
      expanded: {
        y: -7,
      },
      closed: {
        y: -6,
      },
    },
    commitContainer: {
      expanded: {
        y: -7,
        opacity: 1,
      },
      closed: {
        opacity: 0,
      },
    },
  };
};

export const useStyles = makeStyles((theme) => ({
  root: {
    cursor: 'pointer',
    height: '70px',
    width: '100%',
    padding: theme.spacing(2),
    borderRadius: theme.spacing(.5),
    marginTop: theme.spacing(2),
    backgroundColor: theme.palette.dark.blue['200'],
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    '&:hover': {
      border: `1px solid #3A3F47`,
    },
  },
  submissionTag: {
  },
  assignmentName: {
    color: theme.palette.color.blue,
    fontSize: '14px',
    marginTop: '10px',
  },
  commit: {
    fontSize: '13px',
    color: theme.palette.gray['200'],
  },
  tests: {
    fontSize: '14px',
    color: theme.palette.white,
  },
  submittedStatus: {
    fontSize: '14px',
  },
  submittedTime: {
    fontSize: '14px',
  },
  circleIcon: {
    width: '10px',
    height: '10px',
  },
  sucess: {
    color: theme.palette.color.green,
  },
  error: {
    color: theme.palette.color.red,
  },
}));
