import React from "react";
import {makeStyles} from "@material-ui/core/styles";
import CircularProgress from "@material-ui/core/CircularProgress";
import Grid from "@material-ui/core/Grid";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import {Redirect} from "react-router-dom";
import Typography from "@material-ui/core/Typography";
import Zoom from "@material-ui/core/Zoom";
import ReactMarkdownWithHtml from "react-markdown/with-html";
import htmlParser from 'react-markdown/plugins/html-parser';
import {Prism as SyntaxHighlighter} from 'react-syntax-highlighter'
import {dark} from 'react-syntax-highlighter/dist/esm/styles/prism'
// import AceEditor from "react-ace";
import useGet from "../../useGet";
import {useQuery} from "../../utils"

// import "ace-builds/src-min-noconflict/theme-github";
// import "ace-builds/src-min-noconflict/mode-c_cpp";
// import "ace-builds/src-min-noconflict/mode-markdown";

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
  },
  card: {
    minWidth: '512',
  },
}));

const parseHtml = htmlParser({
  isValidNode: (node) => node.type !== 'script',
  processingInstructions: [
    /* ... */
  ]
})

const renderers = {
  code: ({language, value}) => {
    return <SyntaxHighlighter style={dark} language={language} children={value}/>
  }
}

function Question({questions}) {
  const classes = useStyles();
  // const [responses, setResponses] = useState(new Array(...questions.map(question => question.response)));

  return (
    <Grid
      container
      spacing={4}
      className={classes.root}
    >
      <Grid item xs={12}>
        <Card className={classes.card}>
          <CardContent>
            {questions.map((question, index) => (
              <React.Fragment>

                <Typography variant={"h6"}>
                  Question {question.sequence})
                </Typography>

                {/* Question content */}
                <ReactMarkdownWithHtml renderers={renderers} allowDangerousHtml>
                  {question.question}
                </ReactMarkdownWithHtml>

                {/* Question editor */}
                {/*<Grid item xs={12}>*/}
                {/*  <AceEditor*/}
                {/*    mode={question.codeQuestion ? "c_cpp" : "markdown"}*/}
                {/*    theme="github"*/}
                {/*    value={responses[index]}*/}
                {/*    onChange={response => {*/}
                {/*      responses[index] = response*/}
                {/*      setResponses(responses)*/}
                {/*    }}*/}
                {/*  />*/}
                {/*</Grid>*/}

                <br/>
              </React.Fragment>
            ))}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )
}

export default function Questions() {
  const classes = useStyles();
  const query = useQuery();
  const assignmentId = query.get('assignmentId');
  const {loading, error, data} = useGet(`/api/public/assignment/questions/get/${assignmentId}`)

  if (assignmentId === null) return <React.Fragment/>
  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>

  function translateQuestion({response, question}) {
    return {
      question: question.question, codeQuestion: question.code_question, codeLanguage: question.code_language,
      sequence: question.sequence, response: response,
    }
  }

  const questions = data.questions.map(translateQuestion);

  if (questions.length === 0) {
    return <React.Fragment/>
  }

  return (
    <Zoom in={true} timeout={200}>
      <React.Fragment>
        <Typography variant="body1">
          Questions
        </Typography>
        <Question
          questions={questions}
        />
      </React.Fragment>
    </Zoom>
  )
}