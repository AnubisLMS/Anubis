import React, {useState} from 'react';
import Grid from '@material-ui/core/Grid';
import Typography from "@material-ui/core/Typography";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import {Redirect, useParams} from "react-router-dom";

import {api} from '../utils';
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import {makeStyles} from "@material-ui/core/styles";
import Auth from './Auth';

const useStyles = makeStyles(theme => ({
  root: {
    width: '100%',
  },
  title: {
    padding: theme.spacing(0.5),
  }
}));


export default function View() {
  const [data, setData] = useState(null);
  const [authOpen, setAuthOpen] = useState(true);
  const {netid, code} = useParams();
  const classes = useStyles();

  if (!(code || netid)) {
    return <Auth
      open={authOpen}
      onClose={() => setAuthOpen(false)}
    />
  }

  if (data === null) {
    setTimeout(() => {
      api.get(`/finalquestions/${netid}/${code}`).then(res => {
        setData(res.data);
      }).catch(() => null);
    });
    return null;
  }

  if (!data.success || !data.questions) {
    return <Redirect to={'/fq'}/>
  }

  return (
    <Grid container spacing={2} key={`grid-fq`}>
      <Grid item xs={12} key={`fq-title-${netid}`}>
        <Card>
          <CardContent>
            <Typography variant={'h6'} component={'h2'}>
              {`Exam questions for ${netid}`}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      {data.questions.map(({content, level}) => (
        <Grid item xs={12} key={`question-level-${level}`}>
          <ExpansionPanel>
            <ExpansionPanelSummary
              expandIcon={<ExpandMoreIcon/>}
              aria-label="Expand"
              aria-controls={`question-${level}`}
              id={`ep-question-level-${level}`}
            >
              <Typography className={classes.title} variant={'subtitle1'}>
                {`Question ${level}`}
              </Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <div>
                {content.split('\n').map((line, index) => (
                  <Typography
                    key={`q-${level}-line-${index}`}
                    variant={"body1"}
                    color={'textSecondary'}
                    width={100}
                  >
                    {line}
                  </Typography>
                ))}
              </div>
            </ExpansionPanelDetails>
          </ExpansionPanel>
        </Grid>
      ))}
    </Grid>
  );
}