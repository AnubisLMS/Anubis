import React, {useState} from 'react';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';

import ReactMarkdownWithHtml from 'react-markdown/with-html';
import {Prism as SyntaxHighlighter} from 'react-syntax-highlighter';
import {dark} from 'react-syntax-highlighter/dist/esm/styles/prism';
import gfm from 'remark-gfm';
import {makeStyles} from '@material-ui/core/styles';
import Accordion from '@material-ui/core/Accordion';
import AceEditor from 'react-ace';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Grid from '@material-ui/core/Grid';


import 'ace-builds/src-min-noconflict/theme-monokai';
import 'ace-builds/src-min-noconflict/mode-c_cpp';
import 'ace-builds/src-min-noconflict/mode-markdown';
import CardActionArea from '@material-ui/core/CardActionArea';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import axios from 'axios';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import {useSnackbar} from 'notistack';

const useStyles = makeStyles((theme) => ({
  saveButton: {
    margin: theme.spacing(1),
  },
}));

export default function QuestionEditor({question, response, updateResponse, saveResponse}) {
  const classes = useStyles();
  const [showSolution, setShowSolution] = useState(false);

  return (
    <div>
      <Dialog
        open={showSolution}
        onClose={() => setShowSolution(false)}
      >
        <DialogTitle>Question {question.sequence} Solution</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {question?.solution}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSolution(false)} color="primary" autoFocus>
            Close
          </Button>
        </DialogActions>
      </Dialog>
      <Card>
        <CardContent>
          <Typography variant={'subtitle1'}>
          Your Answer:
          </Typography>
          <AceEditor
            mode={question.codeQuestion ? 'c_cpp' : 'markdown'}
            className={classes.editor}
            theme="monokai"
            width={'100%'}
            value={response}
            onChange={updateResponse}
          />
        </CardContent>
        <CardActionArea>
          <Button
            variant={'contained'}
            color={'primary'}
            className={classes.saveButton}
            onClick={saveResponse}
          >
            Save
          </Button>
          {question?.solution ? (
            <Button
              variant={'contained'}
              color={'primary'}
              className={classes.saveButton}
              onClick={() => setShowSolution(true)}
            >
              Show Solution
            </Button>
          ) : null}
        </CardActionArea>
      </Card>
    </div>
  );
}
