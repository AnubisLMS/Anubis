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

export default function QuestionsCard({questions}) {
  const classes = useStyles();

  if (!questions || questions.length === 0) {
    return null;
  }

  return (
    <div className={classes.root}>
      <Grid container justify={'center'} spacing={1}>

        {questions.map((question) => (
          <Grid item xs={12} key={`question-${question.question.pool}`} className={classes.question}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon/>}>
                <div className={classes.icon}>
                  {!question.response || question.response.submitted === null ? (
                    <Tooltip title={'No Submission'}>
                      <RemoveCircleOutlineIcon style={{color: grey[500]}}/>
                    </Tooltip>
                  ) : (
                    question.response.late ? (
                      <Tooltip title={`Submitted late. Last modified ${question.response.submitted}`}>
                        <AssignmentLateIcon style={{color: red[500]}}/>
                      </Tooltip>
                    ) : (
                      <Tooltip title={`Submitted on time. Last modified ${question.response.submitted}`}>
                        <AssignmentTurnedInIcon style={{color: grey[500]}}/>
                      </Tooltip>
                    )
                  )}
                </div>
                <Typography className={classes.heading}>
                  Question {question.question.pool}
                </Typography>
              </AccordionSummary>

              <AccordionDetails>
                {/* Question content */}
                <Grid container spacing={2} direction={'column'}>
                  <QuestionEditor
                    question={question}
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
