import React, {useState} from 'react';
import Grid from '@material-ui/core/Grid';
import {Redirect, useParams} from "react-router-dom";
import {useSnackbar} from 'notistack';

import {api} from '../../../utils';
import Submission from './Submission';
import Error from '../../../Error';
import Build from './Build';
import Tests from '../Test';


export default function SubmissionInfo({data, setData}) {
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
      if (processed) {
        clearInterval(timer.current);
        setData(res.data);
        return;
      }
    }
    setData(res.data);
  };

  const verify = () => {
    if (processed) {
      setData(null);
      setProcessed(false);
    }
    api.get(`/submissions/${commit}/${netid}`).then(res => {
      if (res.data && res.data.success) {
        clearInterval(timer.current);
        timer.current = setInterval(() => (
          api.get(`/submissions/${commit}/${netid}`).then(handler)
        ), 3000);
        handler(res);
      } else if (res.data && !res.data.success) {
        enqueueSnackbar(res.data.error, {variant: 'error', preventDuplicate: true});
        setRedirect('/');
      }
    }).catch(err => null);
  };

  if (redirect)
    return <Redirect to={redirect}/>;

  if (!commit) {
    enqueueSnackbar('invalid commit', {variant: 'error', preventDuplicate: true});
    return <Redirect to={'/'}/>;
  }

  // if (!netid)
  //   return (
  //     <Auth
  //       open={authOpen}
  //       onClose={() => setAuth(false)}
  //       commit={commit}
  //       key={`auth-${commit}-${netid}`}
  //     />
  //   );

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
    enqueueSnackbar(data.error, {variant: 'error', preventDuplicate: true});
    return (
      <Redirect to={'/'}/>
    );
  }

  return (
    <Grid container spacing={2} key={`grid-${processed}`}>
      <Grid item xs={12} key={`submission-${commit}-${netid}-${processed}`}>
        <Submission
          data={submission}
          processed={processed}
          verify={verify}
        />
      </Grid>
      {!errors ? (
        <React.Fragment>
          {tests && reports ?
            <Grid item xs={12} key={`test-${commit}-${netid}-${processed}`}>
              <Tests tests={tests} reports={reports}/>
            </Grid> : null
          }
          {build ?
            <Grid item xs={12} key={`build-${commit}-${netid}-${processed}`}>
              <Build data={build}/>
            </Grid> : null
          }
        </React.Fragment>
      ) : errors ? (
        <Grid item xs={12} key={`error-${commit}-${netid}-${processed}`}>
          <Error data={errors}/>
        </Grid>
      ) : null
      }
    </Grid>
  );
}
