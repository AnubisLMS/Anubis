import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import gfm from 'remark-gfm';
import ReactMarkdownWithHtml from 'react-markdown/with-html';

import Typography from '@material-ui/core/Typography';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Grid from '@material-ui/core/Grid';

import QuestionEditor from './QuestionEditor';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';

import 'ace-builds/src-min-noconflict/theme-monokai';
import 'ace-builds/src-min-noconflict/mode-c_cpp';
import 'ace-builds/src-min-noconflict/mode-markdown';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
  },
  card: {
    minWidth: '512',
  },
  divider: {
    backgroundColor: '#bbb',
  },
  block: {
    display: 'block',
  },
  saveButton: {
    margin: theme.spacing(1),
  },
  markdown: {
    margin: theme.spacing(1),
  },
}));

const saveResponse = (id, response, enqueueSnackbar) => () => {
  axios.post(`/api/public/questions/save/${id}`, {response}).then((resp) => {
    standardStatusHandler(resp, enqueueSnackbar);
  }).catch(standardErrorHandler(enqueueSnackbar));
};

export default function QuestionsCard({questions}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [edits, setEdits] = useState(0);
  const [responses, setResponses] = useState([]);

  const incEdits = () => setEdits((state) => ++state);

  React.useEffect(() => {
    setResponses(questions.map((question) => question.response));
    incEdits();
  }, [questions]);

  if (!questions || questions.length === 0) {
    return null;
  }

  const updateResponse = (index) => (value) => {
    setResponses((state) => {
      state[index] = value;
      return state;
    });
    incEdits();
  };

  return (
    <div className={classes.root}>
      <Grid container justify={'center'} spacing={1}>

        {questions.sort(({question: q1}, {question: q2}) => q1.pool - q2.pool).map(({id, question}, index) => (
          <Grid item xs={12} key={`question-${question.pool}`} className={classes.question}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon/>}>
                <Typography className={classes.heading}>Question {question.pool}</Typography>
              </AccordionSummary>

              <AccordionDetails>
                {/* Question content */}
                <Grid container spacing={2} direction={'column'}>
                  <ReactMarkdownWithHtml
                    className={classes.markdown}
                    plugins={[gfm]}
                    allowDangerousHtml
                  >
                    {question.question}
                  </ReactMarkdownWithHtml>

                  <QuestionEditor
                    question={question}
                    response={responses[index]}
                    updateResponse={updateResponse(index)}
                    saveResponse={saveResponse(id, responses[index], enqueueSnackbar)}
                  />
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>
        ))}
      </Grid>
    </div>
  );
}
