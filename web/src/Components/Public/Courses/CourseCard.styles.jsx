import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles({
  courseCardContainer: {
    flexGrow: 1,
    minWidth: 275,
    maxWidth: 280,
    backgroundColor: '#21262D',
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
    color: '#7A7D81',
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
    fontSize: '12px',
    borderRadius: '3px',
    backgroundColor: '#5686F5',
    padding: '3px 10px 3px',
  },
  totalAssignments: {
    fontSize: '.8rem',
    marginLeft: '10px;',
    color: '#7A7D81',
  },
});
