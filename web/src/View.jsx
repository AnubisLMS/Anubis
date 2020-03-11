import React, {useState} from 'react';
import Grid from '@material-ui/core/Grid';
import {Redirect, useParams} from "react-router-dom";
import {useSnackbar} from 'notistack';

import {api} from './utils';
import Submission from './Submission';
import Auth from './Auth';
import Error from './Error';
import Build from './Build';
import Tests from './Tests';


export default function View() {
  const [data, setData] = useState(null);
  const [authOpen, setAuth] = useState(true);
  const [processed, setProcessed] = React.useState(true);
  const [netid, setNetid] = useState('');
  const {commit} = useParams();
  const {enqueueSnackbar} = useSnackbar();
  const timer = React.useRef();

  React.useEffect(() => {
    return () => {
      clearInterval(timer.current);
    };
  }, []);

  const handler = res => {
    if (res.data && res.data.success) {
      const {submission} = res.data.data;
      const {processed} = submission;
      setProcessed(processed);
      if (processed) clearInterval(timer.current);
    }
    setData(res.data);
  };

  const verify = () => {
    api.get(`/submissions/${commit}/${netid}`).then(res => {
      if (res.data && res.data.success) {
        timer.current = setInterval(() => (
          api.get(`/submissions/${commit}/${netid}`).then(handler)
        ), 5000);
        handler(res);
      }
    }).catch(err => null);
  };

  if (data === null) return (
    <Auth
      open={authOpen}
      onClose={() => setAuth(false)}
      verify={verify}
      commit={commit}
      setNetid={setNetid}
    />
  );

  let submission, reports, build, tests, errors;

  if (data.success) {
    submission = data.data.submission;
    reports = data.data.reports;
    build = data.data.build;
    tests = data.data.tests;
    errors = data.data.errors;
  }

  if (!data.success) {
    enqueueSnackbar(data.error, {variant: 'error'});
    return (
      <Redirect to={'/'}/>
    );
  }

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <Submission
          data={submission}
          processed={processed}
          verify={verify}
        />
      </Grid>
      {processed && !errors ? (
        <React.Fragment>
          <Grid item xs={12}>
            <Tests tests={tests} reports={reports}/>
          </Grid>
          <Grid item xs={12}>
            <Build data={build}/>
          </Grid>
        </React.Fragment>
      ) : errors ? (
        <Grid item xs={12}>
          <Error data={errors}/>
        </Grid>
      ) : null
      }
    </Grid>
  );
}
