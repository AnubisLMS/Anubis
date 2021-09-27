import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  root: {},
  header: {
    paddingTop: theme.spacing(1),
    backgroundColor: theme.palette.dark.black,
    borderBottom: `1px solid ${theme.palette.gray['200']}`,
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingBottom: theme.spacing(4),
  },
  headerLeft: {
    display: 'flex',
    flexDirection: 'row',
  },
  iconOuterCircle: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: '100%',
    width: '60px',
    height: '60px',
    backgroundColor: theme.palette.color.blue,
  },
  iconInnerCircle: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: '100%',
    width: '50px',
    height: '50px',
    backgroundColor: theme.palette.primary.main,
  },
  headerText: {
    marginLeft: theme.spacing(2),
  },
  headerAssignmentName: {
    fontSize: '1.5rem',
  },
  headerCourseName: {
    color: theme.palette.gray['200'],
  },
  headerCourseLink: {
    color: theme.palette.color.blue,
    cursor: 'pointer',
    '&:hover': {
      color: theme.palette.primary.main,
    },
  },
  headerRight: {
    display: 'flex',
    flexDirection: 'row',
  },
  launchIcon: {
    marginRight: theme.spacing(1),
    width: '20px',
    height: '20px',
  },
  ideButton: {
    backgroundColor: theme.palette.primary.main,
    fontSize: '14px',
    borderRadius: '3px',
    padding: `${theme.spacing(1)}px ${theme.spacing(3)}px ${theme.spacing(1)}px`,
  },
  repoButton: {
    fontSize: '14px',
    padding: `${theme.spacing(1)}px ${theme.spacing(3)}px ${theme.spacing(1)}px`,
    backgroundColor: 'transparent',
    border: `1px solid ${theme.palette.primary.main}`,
    borderRadius: '3px',
    color: theme.palette.color.blue,
    '&:hover': {
      backgroundColor: theme.palette.primary.main,
      color: 'white',
    },
    marginLeft: theme.spacing(2),
  },
  content: {
    paddingTop: theme.spacing(4),
  },
  sectionHeader: {
    fontSize: '20px',
  },
  overviewContent: {
    marginTop: theme.spacing(2),
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    width: '100%',
    borderRadius: '3px',
    padding: theme.spacing(2),
  },
  overviewItemTitle: {
    fontSize: '14px',
    letterSpacing: '1px',
    color: theme.palette.gray['200'],
  },
  overviewItemSubtitle: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: theme.spacing(1),
  },
  colorGreen: {
    color: theme.palette.color.green,
  },
  colorRed: {
    color: theme.palette.color.red,
  },
  overviewItemSubtitleText: {
    marginLeft: theme.spacing(1),
  },
  emptyQuestions: {
    marginTop: theme.spacing(2),
    width: '100%',
    height: '150px',
    border: `2px dashed ${theme.palette.dark.blue['200']}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
}));
