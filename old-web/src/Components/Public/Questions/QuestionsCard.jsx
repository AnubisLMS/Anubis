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
import Grid from '@material-ui/core/Grid';
import Tooltip from '@material-ui/core/Tooltip';
import green from '@material-ui/core/colors/green';
import red from '@material-ui/core/colors/red';
import grey from '@material-ui/core/colors/grey';

import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import RemoveCircleOutlineIcon from '@material-ui/icons/RemoveCircleOutline';
import AssignmentTurnedInIcon from '@material-ui/icons/AssignmentTurnedIn';
import AssignmentLateIcon from '@material-ui/icons/AssignmentLate';

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
  icon: {
    marginRight: theme.spacing(1),
  },
}));

const saveResponse = (id, responses, index, setResponses, enqueueSnackbar) => () => {
  axios.post(`/api/public/questions/save/${id}`, {response: responses[index].text}).then((resp) => {
    const data = standardStatusHandler(resp, enqueueSnackbar);
    if (data?.response) {
      setResponses((prev) => {
        prev[index] = data.response;
        return [...prev];
      });
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};

export default function QuestionsCard({questions}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [responses, setResponses] = useState(null);

  React.useEffect(() => {
    setResponses(questions.map((question) => question.response));
  }, [questions]);

  if (!questions || questions.length === 0 || !responses || responses.length === 0) {
    return null;
  }

  const updateResponse = (index) => (value) => {
    setResponses((state) => {
      state[index].text = value;
      return [...state];
    });
  };

  return (
    <div className={classes.root}>
      <Grid container justify={'center'} spacing={1}>

        {questions.map(({
          id, question,
        }, index) => (
          <Grid item xs={12} key={`question-${question.pool}`} className={classes.question}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon/>}>
                <div className={classes.icon}>
                  {responses[index].submitted === null ? (
                    <Tooltip title={'No Submission'}>
                      <RemoveCircleOutlineIcon style={{color: grey[500]}}/>
                    </Tooltip>
                  ) : (
                    responses[index].late ? (
                      <Tooltip title={`Submitted late. Last modified ${responses[index].submitted}`}>
                        <AssignmentLateIcon style={{color: red[500]}}/>
                      </Tooltip>
                    ) : (
                      <Tooltip title={`Submitted on time. Last modified ${responses[index].submitted}`}>
                        <AssignmentTurnedInIcon style={{color: grey[500]}}/>
                      </Tooltip>
                    )
                  )}
                </div>
                <Typography className={classes.heading}>
                  Question {question.pool}
                </Typography>
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
                    response={responses[index].text}
                    updateResponse={updateResponse(index)}
                    saveResponse={saveResponse(id, responses, index, setResponses, enqueueSnackbar)}
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
