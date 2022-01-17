import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(2),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: theme.spacing(1),
  },
  postInfoContainer: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1),
  },
  profilePic: {
    backgroundColor: theme.palette.primary.main,
    padding: theme.spacing(1),
    borderRadius: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '30px',
    height: '30px',
  },
  user: {

  },
  whenPosted: {
    opacity: '.7',
  },
  title: {
    width: '100%',
    fontSize: '28px',
    fontWeight: '600',
  },
  content: {
    width: '100%',
  },
  extraInfo: {
    marginTop: theme.spacing(2),
    width: '100%',
    display: 'flex',
    gap: theme.spacing(3),
    alignItems: 'center',
    opacity: '.8',
  },
  infoContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1),
  },
  icon: {
    fontSize: '14px',
  },
  commentListContainer: {
    padding: theme.spacing(2),
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing(4),
  },
}));

