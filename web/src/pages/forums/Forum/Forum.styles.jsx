import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  controlsContainer: {
    marginTop: theme.spacing(2),
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: theme.spacing(1),
    paddingBottom: theme.spacing(1),
    paddingRight: theme.spacing(3),
    paddingLeft: theme.spacing(3),
    borderRadius: '5px',
    border: `1px solid ${theme.palette.dark.blue['200']}`,
  },
  controlsLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(2),
  },
  courseSelectionContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(2),
  },
  select: {
    paddingLeft: theme.spacing(2),
    paddingRight: theme.spacing(2),
    paddingBottom: theme.spacing(1),
    paddingTop: theme.spacing(1),
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    borderRadius: theme.spacing(.5),
  },
  newPostButton: {
    backgroundColor: theme.palette.primary.main,
    paddingRight: theme.spacing(2),
    paddingLeft: theme.spacing(2),
    paddingTop: theme.spacing(1),
    paddingBottom: theme.spacing(1),
    borderRadius: '2px',
  },
  postsContainer: {
    marginTop: theme.spacing(2),
    width: '100%',
  },
  postListContainer: {
    height: '800px',
    borderLeft: `1px solid ${theme.palette.dark.blue['200']}`,
    borderTop: `1px solid ${theme.palette.dark.blue['200']}`,
    borderBottom: `1px solid ${theme.palette.dark.blue['200']}`,
    borderRadius: '5px 0px 0px 5px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: theme.spacing(1),
    padding: theme.spacing(1),
  },
  postContentContainer: {
    height: '800px',
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    borderRadius: '0px 5px 5px 0px',
  },
}));

