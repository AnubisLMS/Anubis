import React, {useMemo} from 'react';

import Divider from '@material-ui/core/Divider';
import Typography from '@material-ui/core/Typography';
import Close from '@material-ui/icons/Close';
import Cancel from '@material-ui/icons/Cancel';
import Button from '@material-ui/core/Button';
import CheckCircle from '@material-ui/icons/CheckCircle';
import Box from '@material-ui/core/Box';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';

import {Diff, Hunk, markEdits, parseDiff, tokenize} from 'react-diff-view';
import 'react-diff-view/style/index.css';

import {useStyles} from './SubmissionTestExpanded.styles';

const renderToken = (token, defaultRender, i) => {
  switch (token.type) {
  case 'space':
    return (
      <span key={i} className="space">
        {token.children && token.children.map((token, i) => renderToken(token, defaultRender, i))}
      </span>
    );
  default:
    return defaultRender(token, i);
  }
};

export default function SubmissionTestExpanded({
  open,
  testName,
  submissionID,
  assignmentName,
  testSuccess,
  testOutputType,
  testOutput,
  testMessage,
  onClose,
}) {
  const classes = useStyles();
  const diffs = useMemo(() => {
    return parseDiff(testOutput ?? '', {nearbySequences: 'zip'});
  }, [testOutput]);
  const tokens = useMemo(() => {
    if (!!!diffs) return undefined;
    return diffs.map((diff) => tokenize(diff.hunks, {
      hightlight: false,
      enhancers: [markEdits(diffs[0].hunks, {type: 'block'})],
    }));
  }, [diffs]);

  const renderDiffs = ({oldRevision, newRevision, type, hunks, tokens}) => (
    <Diff
      className={classes.testDiff}
      key={`${oldRevision}-${newRevision}`}
      viewType='split'
      diffType={type}
      hunks={hunks || []}
      tokens={tokens}
      renderToken={renderToken}
    >
      {(hunks) => hunks.map((hunk) => <Hunk key={hunk.content} hunk={hunk}/>)}
    </Diff>
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth={'lg'} className={classes.submissionTestExpandedContainer}>
      <div className={classes.testHeader}>
        <Typography className={classes.testName} variant={'h5'}>
          {testName}
        </Typography>
        <Typography className={classes.testName} variant={'h4'}>
          {testMessage}
        </Typography>
        <Typography className={classes.submissionIDTitle}>
          Submission: <span className={classes.submissionID}>{submissionID.substr(0, 10)}</span>
        </Typography>
        <Typography className={classes.assignmentNameTitle}>
          Assignment: <span className={classes.assignmentName}>{assignmentName}</span>
        </Typography>
        <Typography className={classes.testStatus}>
          {testSuccess ?
            <span className={classes.testStatusSuccess}>
              <CheckCircle className={classes.testStatusIcon}/> Test Passed
            </span> :
            <span className={classes.testStatusFail}>
              <Cancel className={classes.testStatusIcon}/> Test Failed
            </span>}
        </Typography>
        <Button onClick={() => onClose()} className={classes.closeIconWrapper}>
          <Close/>
        </Button>
      </div>
      <Divider/>
      <div className={classes.testBody}>
        {testOutputType === 'text' && (
          <Typography className={classes.testOutput}>
            {testOutput ?? ''}
          </Typography>
        )}
        {testOutputType === 'diff' && (
          <React.Fragment>
            <h2>Actual / Expected Output</h2>
            <Box className={classes.diffBox}>
              {diffs && diffs.map((diff, index) => renderDiffs({...diff, tokens: tokens[index]}))}
            </Box>
          </React.Fragment>
        )}
      </div>
    </Dialog>
  );
};

