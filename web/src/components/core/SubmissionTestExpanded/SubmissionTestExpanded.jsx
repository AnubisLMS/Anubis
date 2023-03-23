import React, {useMemo} from 'react';

import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import Close from '@mui/icons-material/Close';
import Cancel from '@mui/icons-material/Cancel';
import Button from '@mui/material/Button';
import CheckCircle from '@mui/icons-material/CheckCircle';
import Box from '@mui/material/Box';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';

import {Diff, Hunk, markEdits, markWord, parseDiff, tokenize} from 'react-diff-view';
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
    if (testOutputType !== 'diff') return [];
    if (!testOutput) return [];
    return parseDiff(testOutput ?? '', {nearbySequences: 'zip'});
  }, [testOutput]);
  const tokens = useMemo(() => {
    if (testOutputType !== 'diff') return [];
    if (!diffs) return [];
    return diffs.map((diff) => tokenize(diff.hunks, {
      hightlight: false,
      enhancers: [
        markEdits(diffs[0].hunks, {type: 'block'}),
        markWord('\0', 'NUL', '␀'),
        markWord('\r', 'CR', '␍'),
      ],
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
            <h2>Expected / Actual Output</h2>
            <Box className={classes.diffBox}>
              {diffs && diffs.map((diff, index) => renderDiffs({...diff, tokens: tokens[index]}))}
            </Box>
          </React.Fragment>
        )}
      </div>
    </Dialog>
  );
};

