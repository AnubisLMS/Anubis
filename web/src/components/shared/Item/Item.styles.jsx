import {makeStyles} from '@mui/material/styles';

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
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    '&:hover': {
      border: `1px solid #3A3F47`,
    },
  },
  titleBlockContainer: {
    display: 'flex',
    width: '100%',
    alignItems: 'center',
  },
  titleIconContainer: {
    marginRight: theme.spacing(2),
    opacity: .7,
  },
  block: {
    display: 'flex',
    alignItems: 'center',
    width: '100%',
  },
  end: {
    justifyContent: 'flex-end',
  },
  center: {
    justifyContent: 'center',
  },
  title: {
    color: theme.palette.color.blue,
    fontSize: '14px',
    marginTop: '10px',
  },
  subTitle: {
    fontSize: '13px',
    color: theme.palette.color.gray,
  },
  statusIcon: {
    width: '10px',
    height: '10px',
  },
  orange: {
    color: theme.palette.color.orange,
  },
  red: {
    color: theme.palette.color.orange,
  },
  green: {
    color: theme.palette.color.green,
  },
  blue: {
    color: theme.palette.color.blue,
  },
}));
