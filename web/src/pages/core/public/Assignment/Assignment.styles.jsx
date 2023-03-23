import makeStyles from '@mui/styles/makeStyles';
import grey from '@mui/material/colors/grey';

export const useStyles = makeStyles((theme) => ({
  root: {},
  header: {
    paddingTop: theme.spacing(2),
    backgroundColor: theme.palette.dark.black,
    borderBottom: `1px solid ${theme.palette.color.gray}`,
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
    color: theme.palette.color.gray,
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
    fontSize: '14px',
    borderRadius: '3px',
    padding: `${theme.spacing(1)} ${theme.spacing(3)} ${theme.spacing(1)}`,
  },
  repoButton: {
    fontSize: '14px',
    borderRadius: '3px',
    padding: `${theme.spacing(1)} ${theme.spacing(3)} ${theme.spacing(1)}`,
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
    color: theme.palette.color.gray,
  },
  overviewItemSubtitle: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: theme.spacing(1),
  },
  colorOrange: {
    color: theme.palette.color.orange,
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
    minHeight: '150px',
    border: `2px dashed ${theme.palette.dark.blue['200']}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  markdown: {
    margin: theme.spacing(1),
    color: theme.palette.color.gray,
  },
}));
