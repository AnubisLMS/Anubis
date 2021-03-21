import React from 'react';
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

import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import downloadTextFile from '../../../Utils/downloadTextFile';

const useStyles = makeStyles((theme) => ({
  button: {
    margin: theme.spacing(1),
  },
}));

const resetWarning = 'Delete all question assignments. ' +
  'This action can not be undone. ' +
  'After assigning new questions, students may have a different set of assigned questions. ' +
  'Do not use this if you are not sure what you are doing.';

export default function QuestionControls({uniqueCode}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  const assignQuestions = () => {
    axios.get(`/api/admin/questions/assign/${uniqueCode}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const hardResetQuestions = () => {
    axios.get(`/api/admin/questions/assign/${uniqueCode}`).then((response) => {
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
          <Grid item xs={12}>
            <Tooltip title={resetWarning}>
              <Button
                fullWidth
                startIcon={<DeleteForeverIcon/>}
                color={'secondary'}
                variant={'contained'}
                onClick={hardResetQuestions}
              >
                Hard Reset Question Assignments
              </Button>
            </Tooltip>
          </Grid>

        </Grid>
      </CardContent>
    </Card>
  );
}
