import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing(1),
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1),
  },
  commentedWhen: {
    opacity: '.8',
  },
  profilePic: {
    width: '20px',
    height: '20px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.palette.primary.main,
    borderRadius: '100%',
  },
  profilePicText: {
    fontSize: '12px',
  },
  content: {
    fontSize: '16px',
  },
}));

