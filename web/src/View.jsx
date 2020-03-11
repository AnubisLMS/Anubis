import React, {useState} from 'react';
import Grid from '@material-ui/core/Grid';
import {Redirect, useParams} from "react-router-dom";
import {useSnackbar} from 'notistack';
import Grow from '@material-ui/core/Grow';

import {api} from './utils';
import Submission from './Submission';
import Auth from './Auth';
import Error from './Error';
import Build from './Build';
import Tests from './Tests';


export default function View() {
  const [data, setData] = useState(null);
  const [authOpen, setAuth] = useState(true);
  const [processed, setProcessed] = useState(true);
  const [redirect, setRedirect] = useState('');
  const {commit, netid} = useParams();
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
      } else if (res.data && !res.data.success) {
        enqueueSnackbar(res.data.error, {variant: 'error'});
        setRedirect('/');
      }
    }).catch(err => null);
  };

  if (redirect)
    return <Redirect to={redirect} />;

  if (!commit) {
    enqueueSnackbar('invalid commit', {variant: 'error'});
    return <Redirect to={'/'} />;
  }

  if (!netid)
    return (
      <Auth
        open={authOpen}
        onClose={() => setAuth(false)}
        commit={commit}
      />
    );

  let submission, reports, build, tests, errors;

  if (!data) {
    verify();
    return <div/>;
  }

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
