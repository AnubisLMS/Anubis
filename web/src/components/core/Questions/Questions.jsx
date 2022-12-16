import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import Typography from '@mui/material/Typography';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import Box from '@mui/material/Box';
import makeStyles from '@mui/styles/makeStyles';
import DialogActions from '@mui/material/DialogActions';
import gfm from 'remark-gfm';
import Button from '@mui/material/Button';
import ReactMarkdownWithHtml from 'react-markdown/with-html';
import QuestionItem from './QuestionItem';
import QuestionEditor from './QuestionEditor';

import 'ace-builds/src-min-noconflict/theme-monokai';
import 'ace-builds/src-min-noconflict/mode-c_cpp';
import 'ace-builds/src-min-noconflict/mode-markdown';
import Dialog from '@mui/material/Dialog';


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
  emptyQuestions: {
    marginTop: theme.spacing(2),
    width: '100%',
    minHeight: '150px',
    border: `2px dashed ${theme.palette.dark.blue['200']}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
}));

export default function Questions({assignment_id}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [questions, setQuestions] = useState([]);
  const [selectedQuestionId, setSelectedQuestionId] = useState(null);

  React.useEffect(() => {
    axios.get(`/api/public/questions/get/${assignment_id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.questions) {
        setQuestions(data.questions);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  const updateResponse = (questionId) => (value) => {
    setQuestions((prev) => {
      for (const item of prev) {
        if (item.id === questionId) {
          if (!item.response) {
            item.response = {text: value};
          } else {
            item.response.text = value;
          }
          break;
        }
      }
      return [...prev];
    });
  };

  const saveResponse = () => {
    axios.post(`/api/public/questions/save/${assignment_id}`, {questions}).then((resp) => {
      const data = standardStatusHandler(resp, enqueueSnackbar);
      if (data?.questions) {
        setQuestions([...data.questions]);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const selectedQuestion = (id) => {
    for (const item of questions) {
      if (item.id === id) {
        return item;
      }
    }
    return {};
  };

  if (questions.length === 0) {
    return (
      <Box className={classes.emptyQuestions}>
        <Typography className={classes.emptyQuestionsText}>
          Oh no! There are no questions for this assignment.
        </Typography>
      </Box>
    );
  }

  return (
    <React.Fragment>
      {questions.map((question, index) => (
        <QuestionItem
          key={index}
          question={question}
          onClick={() => {
            setSelectedQuestionId(question.id);
          }}
        />
      ))}
      <Dialog open={!!selectedQuestionId} onClose={() => {
        saveResponse();
        setSelectedQuestionId(null);
      }} maxWidth={'lg'}>
        {selectedQuestionId && (
          <Box sx={{ml: 2, mr: 2}}>
            <ReactMarkdownWithHtml
              className={classes.markdown}
              remarkPlugins={[gfm]}
              allowDangerousHtml
            >
              {selectedQuestion(selectedQuestionId).question}
            </ReactMarkdownWithHtml>
            <QuestionEditor
              question={selectedQuestion(selectedQuestionId)}
              updateResponse={updateResponse(selectedQuestionId)}
              saveResponse={saveResponse}
              // commands={[{ // commands is array of key bindings.
              //   name: 'save', // name for the key binding.
              //   bindKey: {win: 'Ctrl-s', mac: 'Command-s'}, // key combination used for the command.
              //   exec: saveResponse, // function to execute when keys are pressed.
              // }]}
            />
            <DialogActions>
              <Button
                variant={'contained'}
                color={'primary'}
                className={classes.saveButton}
                onClick={saveResponse}
              >
                Save
              </Button>
              {selectedQuestion(selectedQuestionId)?.question?.solution ? (
                <Button
                  variant={'contained'}
                  color={'primary'}
                  className={classes.saveButton}
                  onClick={() => setShowSolution(true)}
                >
                  Show Solution
                </Button>
              ) : null}
            </DialogActions>
          </Box>
        )}
      </Dialog>
    </React.Fragment>
  );
}
