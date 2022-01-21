import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    marginTop: theme.spacing(2),
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
    opacity: '.7',
    fontSize: '11px',
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
  replyActions: {
    opacity: '.7',
    fontSize: '14px',
    display: 'flex',
    gap: theme.spacing(1),
  },
  action: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(.2),
    cursor: 'pointer',
  },
  icon: {
    width: '12px',
  },
  actionItem: {
    fontSize: '11px',
  },
}));

