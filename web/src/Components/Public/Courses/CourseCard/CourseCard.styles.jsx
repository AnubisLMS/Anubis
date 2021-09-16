import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  courseCardContainer: {
    color: theme.palette.white,
    flexGrow: 1,
    minWidth: 275,
    maxWidth: 280,
    backgroundColor: theme.palette.dark.blue['200'],
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    padding: '20px',
    borderRadius: '10px',
  },
  courseName: {
    fontSize: '20px',
  },
  instructorName: {
    color: theme.palette.gray['200'],
    fontSize: '16px',
  },
  courseActionsContainer: {
    marginTop: '20px',
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
  },
  openCourseButton: {
    fontSize: '14px',
    borderRadius: '3px',
    backgroundColor: theme.palette.primary.main,
    padding: '5px 10px 5px',
  },
  totalAssignments: {
    fontSize: '.8rem',
    marginLeft: '10px;',
    color: theme.palette.gray['200'],
  },
}));
