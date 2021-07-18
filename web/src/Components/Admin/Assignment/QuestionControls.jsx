import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Tooltip from '@material-ui/core/Tooltip';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CardHeader from '@material-ui/core/CardHeader';

import CloudDownload from '@material-ui/icons/CloudDownload';
import DeleteForeverIcon from '@material-ui/icons/DeleteForever';
import AssignmentIndIcon from '@material-ui/icons/AssignmentInd';
import AddIcon from '@material-ui/icons/Add';
import ArchiveIcon from '@material-ui/icons/Archive';

import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import downloadTextFile from '../../../Utils/downloadTextFile';

const resetWarning = (
  <div>
    <p>
      This will delete all question assignments. This action cannot be easily undone.
      After assigning new questions, students may have a different set of assigned questions.
      Consider downloading the question assignments before running this action.
    </p>
    <p style={{color: 'red'}}> Do not use this if you are not sure what you are doing. </p>
  </div>
);

const hardResetWarning = (
  <div>
    <p>
      This will delete all assignments and questions for the assignments. This action cannot be easily undone.
      You will need to re-sync the assignment to get the questions back.
      Consider downloading the question assignments before running this action.
    </p>
    <p style={{color: 'red'}}> Do not use this if you are not sure what you are doing. </p>
  </div>
);

export default function QuestionControls({assignmentId, reload, questionsAssigned, assignmentName}) {
  const {enqueueSnackbar} = useSnackbar();
  const [verify, setVerify] = useState(null);

  const assignQuestions = () => {
    axios.get(`/api/admin/questions/assign/${assignmentId}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
      reload();
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const hardResetQuestions = () => {
    axios.get(`/api/admin/questions/hard-reset/${assignmentId}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
      reload();
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const resetQuestionAssignments = () => {
    axios.get(`/api/admin/questions/reset-assignments/${assignmentId}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
      reload();
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const downloadQuestionAssignments = () => {
    axios.get(`/api/admin/questions/get-assignments/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.assignments) {
        downloadTextFile(
          `assignment-${assignmentName}-question-assignments.json`,
          JSON.stringify(data.assignments),
          'application/json',
        );
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const addQuestion = () => {
    axios.get(`/api/admin/questions/add/${assignmentId}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
      reload();
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
          <Button onClick={() => (
            setVerify(null)
          )} color="primary" variant={'contained'} autoFocus>
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
        <CardHeader
          title={`Questions for ${assignmentName}`}
          subheader={questionsAssigned ?
            'Questions are assigned' :
            'Questions are not assigned'
          }
        />
        <CardContent>
          <Grid container spacing={2}>

            {/* Assign questions button */}
            <Grid item xs={12} sm={6} md={3}>
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

            {/* Add question button */}
            <Grid item xs={12} sm={6} md={3}>
              <Tooltip title={'Add question'}>
                <Button
                  fullWidth
                  startIcon={<AddIcon/>}
                  color={'primary'}
                  variant={'contained'}
                  onClick={addQuestion}
                >
                  Add New Question
                </Button>
              </Tooltip>
            </Grid>

            {/* Reset questions icon */}
            <Grid item xs={12} sm={6} md={3}>
              <Tooltip title={'Download question assignments'}>
                <Button
                  fullWidth
                  startIcon={<CloudDownload/>}
                  color={'primary'}
                  variant={'contained'}
                  onClick={downloadQuestionAssignments}
                >
                  Assignments (json)
                </Button>
              </Tooltip>
            </Grid>

            {/* Download assignments icon */}
            <Grid item xs={12} sm={6} md={3}>
              <Tooltip title={'Download question assignments'}>
                <Button
                  fullWidth
                  startIcon={<ArchiveIcon/>}
                  color={'primary'}
                  variant={'contained'}
                  component={'a'}
                  href={`/api/admin/questions/export/${assignmentId}`}
                  download
                >
                  Assignments (zip)
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
