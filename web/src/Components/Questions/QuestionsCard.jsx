import CardContent from '@material-ui/core/CardContent';
import React from 'react';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';

import ReactMarkdownWithHtml from 'react-markdown/with-html';
import {Prism as SyntaxHighlighter} from 'react-syntax-highlighter';
import {dark} from 'react-syntax-highlighter/dist/esm/styles/prism';
import {makeStyles} from '@material-ui/core/styles';


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

const renderers = {
  // eslint-disable-next-line react/display-name
  code: ({language, value}) => {
    return (
      <SyntaxHighlighter style={dark} language={language}>
        {value}
      </SyntaxHighlighter>
    );
  },
};

export default function QuestionsCard({questions}) {
  const classes = useStyles();

  return (
    <Card className={classes.card}>
      <CardContent>
        {questions.map((question, index) => (
          <div key={`question-${index}`}>

            <Typography variant={'h6'}>
              Question {question.sequence})
            </Typography>

            {/* Question content */}
            <ReactMarkdownWithHtml renderers={renderers} allowDangerousHtml>
              {question.question}
            </ReactMarkdownWithHtml>

            {/* Question editor */}
            {/* <Grid item xs={12}>*/}
            {/*  <AceEditor*/}
            {/*    mode={question.codeQuestion ? "c_cpp" : "markdown"}*/}
            {/*    theme="github"*/}
            {/*    value={responses[index]}*/}
            {/*    onChange={response => {*/}
            {/*      responses[index] = response*/}
            {/*      setResponses(responses)*/}
            {/*    }}*/}
            {/*  />*/}
            {/* </Grid>*/}

            <br/>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
