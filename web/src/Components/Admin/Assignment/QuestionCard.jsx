import React from 'react';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/theme-monokai';
import 'ace-builds/src-noconflict/mode-markdown';
import gfm from 'remark-gfm';
import ReactMarkdownWithHtml from 'react-markdown/with-html';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Input from '@material-ui/core/Input';
import TextField from '@material-ui/core/TextField';
import SaveIcon from '@material-ui/icons/Save';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';
import DeleteForeverIcon from '@material-ui/icons/DeleteForever';
import clsx from 'clsx';


const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  preview: {
    height: '100%',
    width: '100%',
  },
  padding1: {
    padding: theme.spacing(1),
  },
  padding2: {
    padding: theme.spacing(2),
  },
  margin1: {
    margin: theme.spacing(1),
  },
  input: {
    position: 'relative',
    width: 42,
    marginLeft: theme.spacing(2),
  },
  code_lang: {
    marginLeft: theme.spacing(1),
    minWidth: 300,
  },
}));

export default function QuestionCard({assignmentQuestion, updateQuestion, saveQuestion, deleteQuestion, reload}) {
  const classes = useStyles();
  const {
    pool = 0,
    question = '',
    solution = '',
    code_language = '',
    code_question = false,
  } = assignmentQuestion;

  return (
    <Card>
      <CardContent>
        <Grid container spacing={2}>

          <Grid item xs={12}>
            <Typography style={{display: 'inline'}}>
              Question Pool
            </Typography>
            <Input
              className={classes.input}
              value={pool}
              onChange={(e) => (
                updateQuestion({...assignmentQuestion, pool: e.target.value})
              )}
              margin="dense"
              inputProps={{
                'step': 1,
                'min': 0,
                'type': 'number',
              }}
            />
          </Grid>

          <Grid item xs={12}>
            <div style={{display: 'flex'}}>
              <FormControlLabel
                value={code_question}
                control={
                  <Switch
                    checked={code_question}
                    color={'primary'}
                    onClick={() => updateQuestion({...assignmentQuestion, code_question: !code_question})}
                  />
                }
                label={'Code Question'}
                labelPlacement="start"
              />

              <TextField
                variant={'outlined'}
                label={'Code Language (markdown, cpp)'}
                value={code_language}
                className={classes.code_lang}
                onChange={(e) => (
                  updateQuestion({...assignmentQuestion, code_language: e.target.value})
                )}
              />
            </div>
          </Grid>
        </Grid>

        <Grid container spacing={2} direction={'row'} justify={'center'} className={classes.padding1}>
          <Grid item sm={12} md={6}>
            <Typography variant={'body1'}>
              Question Editor
            </Typography>
            <AceEditor
              mode={'markdown'}
              theme={'monokai'}
              onChange={(e) => updateQuestion({...assignmentQuestion, question: e})}
              value={question}
              height={400}
              width={'100%'}
              editorProps={{$blockScrolling: true}}
            />
          </Grid>
          <Grid item sm={12} md={6}>
            <Typography variant={'body1'}>
              Markdown Preview
            </Typography>
            <ReactMarkdownWithHtml
              className={classes.markdown}
              plugins={[gfm]}
              allowDangerousHtml
            >
              {question}
            </ReactMarkdownWithHtml>
          </Grid>
        </Grid>

        <Grid container spacing={2} direction={'row'} justify={'center'} className={classes.padding1}>
          <Grid item sm={12} md={6}>
            <Typography variant={'body1'}>
              Solution Editor
            </Typography>
            <Typography variant={'body2'} color={'textSecondary'} style={{fontSize: 12}}>
              Solutions only visible to TAs
            </Typography>
            <AceEditor
              mode={'markdown'}
              theme={'monokai'}
              onChange={(e) => updateQuestion({...assignmentQuestion, solution: e})}
              value={solution}
              height={400}
              width={'100%'}
              editorProps={{$blockScrolling: true}}
            />
          </Grid>
          <Grid item sm={12} md={6}>
            <Typography variant={'body1'}>
              Markdown Preview
            </Typography>
            <ReactMarkdownWithHtml
              className={classes.markdown}
              plugins={[gfm]}
              allowDangerousHtml
            >
              {solution}
            </ReactMarkdownWithHtml>
          </Grid>
        </Grid>

      </CardContent>
      <CardActions>
        <Button
          size="small"
          color={'primary'}
          variant={'contained'}
          startIcon={<SaveIcon/>}
          onClick={saveQuestion}
        >
          Save
        </Button>
        <Button
          size="small"
          color={'secondary'}
          variant={'contained'}
          startIcon={<DeleteForeverIcon/>}
          onClick={deleteQuestion}
        >
          Delete
        </Button>
      </CardActions>
    </Card>
  );
}
