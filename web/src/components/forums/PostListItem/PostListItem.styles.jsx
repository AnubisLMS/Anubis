import makeStyles from '@mui/styles/makeStyles';

export const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(1),
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    borderRadius: '3px',
    width: '100%',
    display: 'flex',
    overflow: 'hidden',
    alignItems: 'center',
    gap: theme.spacing(1.5),
    cursor: 'pointer',
    '&:hover': {
      backgroundColor: theme.palette.dark.blue['100'],
    },
  },
  selected: {
    border: `1px solid ${theme.palette.primary.main}`,
    backgroundColor: theme.palette.dark.blue['200'],
  },
  title: {
    fontSize: '16px',
    lineHeight: '16px',
    fontWeight: '600',
  },
  seenIcon: {
    color: theme.palette.primary.main,
    width: '12px',
    height: '12px',
  },
  content: {
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'column',
    justifyContent: 'center',
    gap: '5px',
  },
  summary: { // i want two lines of text
    margin: 0,
    opacity: '.8',
    fontSize: '0.8rem',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  dataSummary: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    opacity: '.8',
  },
  dotDivider: {
    fontSize: '6px',
    opacity: '.7',
  },
  infoContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    fontSize: '0.8rem',
  },
  icon: {
    fontSize: '14px',
  },
}));
