import makeStyles from '@mui/styles/makeStyles';

export const useStyles = makeStyles((theme) => ({
  container: {
    width: '100%',
    display: 'flex',
    marginTop: theme.spacing(2),
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: theme.spacing(2),
    backgroundColor: theme.palette.dark.blue['100'],
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    borderRadius: `${theme.spacing(1)} ${theme.spacing(1)} 0px 0px`,
  },
  sectionBlock: {
    display: 'flex',
    alignItems: 'center',
    width: '100%',
  },
  start: {
    justifyContent: 'flex-start',
  },
  end: {
    justifyContent: 'flex-end',
  },
  center: {
    justifyContent: 'center',
  },
}));
