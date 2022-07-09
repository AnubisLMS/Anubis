import makeStyles from '@mui/styles/makeStyles';

export const useStyles = makeStyles((theme) => ({
  submissionTestExpandedContainer: {
    width: '100%',
    minHeight: '400px',
    color: theme.palette.white,
    // backgroundColor: theme.palette.dark.blue['200'],
    borderRadius: theme.spacing(1.25),
  },
  testHeader: {
    borderBottom: '1px',
    borderColor: theme.palette.color.gray,
    padding: `${theme.spacing(3)} ${theme.spacing(6)}`,
    verticalAlign: 'middle',
  },
  testName: {
    display: 'inline',
    fontSize: '18px',
    color: theme.palette.white,
    paddingRight: theme.spacing(3),
    width: 'fit-content',
  },
  submissionIDTitle: {
    color: theme.palette.color.gray,
    display: 'inline',
    fontSize: '14px',
    padding: `0px ${theme.spacing(3)}`,
    width: 'fit-content',
  },
  submissionID: {
    color: theme.palette.white,
  },
  assignmentNameTitle: {
    color: theme.palette.color.gray,
    display: 'inline',
    fontSize: '14px',
    padding: `0px ${theme.spacing(3)}`,
    width: 'fit-content',
  },
  assignmentName: {
    color: theme.palette.white,
  },
  testStatus: {
    display: 'inline',
    fontSize: '14px',
    padding: `0px ${theme.spacing(3)}`,
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
    padding: `${theme.spacing(3)} ${theme.spacing(6)}`,
  },
  testOutputTitle: {
    color: theme.palette.white,
    fontSize: '18px',
    paddingBottom: theme.spacing(3),
  },
  testOutput: {
    color: theme.palette.color.gray,
    whiteSpace: 'pre-line',
    fontSize: '16px',
    paddingBottom: theme.spacing(3),
  },
  testDiff: {
    color: 'black',
    borderRadius: '10px',
  },
  diffBox: {
    backgroundColor: 'white',
    minHeight: '200px',
  },
  '@global': {
    '.diff-code-delete, .diff-gutter-delete, .diff-code-insert, .diff-gutter-insert': {
      color: 'black',
    },
  },
}));

