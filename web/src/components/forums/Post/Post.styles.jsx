import makeStyles from '@mui/styles/makeStyles';

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
  infoToolbar: {
    display: 'flex',
    gap: theme.spacing(3),
    alignItems: 'center',
  },
  extraInfo: {
    marginTop: theme.spacing(2),
    width: '100%',
    display: 'flex',
    gap: theme.spacing(3),
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  infoContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1),
    opacity: '.8',
  },
  icon: {
    fontSize: '14px',
  },
  commentListContainer: {
    paddingTop: theme.spacing(2),
    width: '100%',
  },
  addComment: {
    height: '100%',
    backgroundColor: theme.palette.primary.main,
    paddingRight: theme.spacing(2),
    paddingLeft: theme.spacing(2),
    paddingTop: theme.spacing(1),
    paddingBottom: theme.spacing(1),
    borderRadius: '15px',
    color: theme.palette.white,
    '&:hover': {
      color: theme.palette.primary.main,
    },
  },
  commentEditor: {
    width: '500px',
  },
}));

