import {makeStyles} from '@mui/material/styles';

export const useStyles = makeStyles((theme) => ({
  submissionSummaryContainer: {
    width: '100%',
    paddingTop: theme.spacing(3),
    paddingBottom: theme.spacing(3),
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
    position: 'relative',
    borderRadius: theme.spacing(1),
    padding: `${theme.spacing(0)}px ${theme.spacing(2)}px ${theme.spacing(0)}px ${theme.spacing(2)}px`,
  },
  assignmentName: {
    color: theme.palette.white,
    fontSize: '18px',
    fontWeight: 'Normal',
    marginRight: theme.spacing(2),
    whiteSpace: 'nowrap',
  },
  dataContainer: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
  },
  dataItem: {
    marginLeft: theme.spacing(1),
    marginRight: theme.spacing(1),
  },
  textLabel: {
    fontWeight: 'Regular',
    fontSize: '13px',
    color: theme.palette.color.gray,
    marginRight: theme.spacing(.5),
    whiteSpace: 'nowrap',
  },
  textContent: {
    fontWeight: 'Regular',
    fontSize: '13px',
    color: theme.palette.color.white,
    marginRight: theme.spacing(2),
    whiteSpace: 'nowrap',
  },
  submittedStatus: {
    fontSize: '13px',
    display: 'flex',
  },
  circleIcon: {
    width: '25px',
    height: '20px',
  },
  success: {
    color: theme.palette.color.green,
  },
  error: {
    color: theme.palette.color.red,
  },
}));
