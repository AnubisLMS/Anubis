import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Tooltip from '@material-ui/core/Tooltip';
import CloudDownload from '@material-ui/icons/CloudDownload';
import DeleteForeverIcon from '@material-ui/icons/DeleteForever';
import AssignmentIndIcon from '@material-ui/icons/AssignmentInd';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import downloadTextFile from '../../../Utils/downloadTextFile';

const resetWarning = 'This will delete all question assignments. ' +
  'This action cannot be undone. ' +
  'After assigning new questions, students may have a different set of assigned questions. ' +
  'Do not use this if you are not sure what you are doing.';

const hardResetWarning = 'This will delete all assignments and questions for the assignments. ' +
  'This action cannot be undone. ' +
  'You will need to re-sync the assignment to get the questions back. ' +
  'Do not use this fi you are not sure what you are doing.';

export default function QuestionControls({uniqueCode}) {
  const {enqueueSnackbar} = useSnackbar();
  const [verify, setVerify] = useState(null);


  const assignQuestions = () => {
    axios.get(`/api/admin/questions/assign/${uniqueCode}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const hardResetQuestions = () => {
    axios.get(`/api/admin/questions/hard-reset/${uniqueCode}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const resetQuestionAssignments = () => {
    axios.get(`/api/admin/questions/reset-assignments/${uniqueCode}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const downloadQuestionAssignments = () => {
    axios.get(`/api/admin/questions/get-assignments/${uniqueCode}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.questions) {
        downloadTextFile(
          `assignment-${uniqueCode}-question-assignments.json`,
          JSON.stringify(data.questions),
          'application/json',
        );
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  return (
    <React.Fragment>
      <Dialog
        open={!!verify}
        onClose={() => setVerify(null)}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{verify?.title}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            {verify?.content}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVerify(null)} color="primary" variant={'contained'} autoFocus>
            Cancel
          </Button>
          <Button onClick={() => {
            verify.action();
            setVerify(null);
          }} color="secondary" variant={'contained'}>
            Proceed
          </Button>
        </DialogActions>
      </Dialog>
      <Card>
        <CardContent>
          <Grid container spacing={2}>

            {/* Assign questions button */}
            <Grid item xs={12} sm={6}>
              <Tooltip title={'Assign questions to students'}>
                <Button
                  fullWidth
                  startIcon={<AssignmentIndIcon/>}
                  color={'primary'}
                  variant={'contained'}
                  onClick={assignQuestions}
                >
                Assign Questions
                </Button>
              </Tooltip>
            </Grid>

            {/* Reset questions icon */}
            <Grid item xs={12} sm={6}>
              <Tooltip title={'Download question assignments'}>
                <Button
                  fullWidth
                  startIcon={<CloudDownload/>}
                  color={'primary'}
                  variant={'contained'}
                  onClick={downloadQuestionAssignments}
                >
                Download question assignments
                </Button>
              </Tooltip>
            </Grid>

            {/* Reset questions icon */}
            <Grid item xs={12} sm={6}>
              <Tooltip title={resetWarning}>
                <Button
                  fullWidth
                  startIcon={<DeleteForeverIcon/>}
                  color={'secondary'}
                  variant={'contained'}
                  onClick={() => setVerify({
                    title: 'Reset Question Assignments',
                    content: resetWarning,
                    action: resetQuestionAssignments,
                  })}
                >
                Reset Question Assignments
                </Button>
              </Tooltip>
            </Grid>

            {/* Reset questions icon */}
            <Grid item xs={12} sm={6}>
              <Tooltip title={hardResetWarning}>
                <Button
                  fullWidth
                  startIcon={<DeleteForeverIcon/>}
                  color={'secondary'}
                  variant={'contained'}
                  onClick={() => setVerify({
                    title: 'Hard Reset Warning',
                    content: hardResetWarning,
                    action: hardResetQuestions,
                  })}
                >
                Hard Reset Questions
                </Button>
              </Tooltip>
            </Grid>

          </Grid>
        </CardContent>
      </Card>
    </React.Fragment>
  );
}
