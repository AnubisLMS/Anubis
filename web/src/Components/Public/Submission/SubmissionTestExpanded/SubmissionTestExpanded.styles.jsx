import {makeStyles} from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  submissionTestExpandedContainer: {
    color: theme.palette.white,
    backgroundColor: theme.palette.dark.blue['200'],
    borderRadius: `${theme.spacing(1.25)}px`,
  },
  testHeader: {
    borderBottom: '1px',
    borderColor: theme.palette.gray['100'],
    padding: `${theme.spacing(3)}px ${theme.spacing(6)}px`,
    verticalAlign: 'middle',
  },
  testName: {
    display: 'inline',
    color: theme.palette.white,
    paddingRight: `${theme.spacing(3)}px`,
    width: 'fit-content',
  },
  submissionIDTitle: {
    color: theme.palette.gray['200'],
    display: 'inline',
    fontSize: '14px',
    padding: `0px ${theme.spacing(3)}px`,
    width: 'fit-content',
  },
  submissionID: {
    color: theme.palette.white,
  },
  assignmentNameTitle: {
    color: theme.palette.gray['200'],
    display: 'inline',
    fontSize: '14px',
    padding: `0px ${theme.spacing(3)}px`,
    width: 'fit-content',
  },
  assignmentName: {
    color: theme.palette.white,
  },
  testStatus: {
    display: 'inline',
    fontSize: '14px',
    padding: `0px ${theme.spacing(3)}px`,
    width: 'fit-content',
  },
  testStatusSuccess: {
    color: theme.palette.color.green,
  },
  testStatusFail: {
    color: theme.palette.color.red,
  },
  testStatusIcon: {
    verticalAlign: 'middle',
    height: '14px',
    width: '14px',
  },
  closeIconWrapper: {
    display: 'flex',
    alignContent: 'center',
    float: 'right',
    verticalAlign: 'middle',
  },
  testBody: {
    padding: `${theme.spacing(3)}px ${theme.spacing(6)}px`,
  },
  testOutputTitle: {
    color: theme.palette.white,
    fontSize: '18px',
    paddingBottom: `${theme.spacing(3)}px`,
  },
  testOutput: {
    color: theme.palette.gray['100'],
    fontSize: '16px',
    paddingBottom: `${theme.spacing(3)}px`,
  },
}));

