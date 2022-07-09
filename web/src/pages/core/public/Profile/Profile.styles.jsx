import {makeStyles} from '@mui/styles';

export const useStyles = makeStyles((theme) => ({
  fieldsContainer: {
    marginTop: theme.spacing(3),
    width: '100%',
  },
  githubContainer: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    padding: theme.spacing(2),
    borderRadius: theme.spacing(.5),
  },
  githubText: {
    fontSize: '16px',
  },
  saveButton: {
    backgroundColor: theme.palette.primary.main,
    borderRadius: theme.spacing(.5),
  },
  bioContainer: {
    marginTop: theme.spacing(3),
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  rowFlex: {
    display: 'flex',
    alignItems: 'center',
  },
  userGroup: {
    marginLeft: theme.spacing(1),
    backgroundColor: theme.palette.dark.blue['200'],
    borderRadius: theme.spacing(1),
    padding: theme.spacing(1),
  },
  super: {
    color: theme.palette.color.red,
  },
  admin: {
    color: theme.palette.color.orange,
  },
  profilePic: {
    width: '60px',
    height: '60px',
    borderRadius: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.palette.primary.main,
  },
  letter: {
    fontSize: '36px',
  },
  profileText: {
    marginLeft: theme.spacing(2),
  },
  name: {
    fontSize: '24px',
  },
  netid: {
    opacity: '.8',
    marginTop: -theme.spacing(.5),
  },
}));

