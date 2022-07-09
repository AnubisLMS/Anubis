import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {useParams} from 'react-router-dom';

import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import Fab from '@mui/material/Fab';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import yellow from '@mui/material/colors/yellow';

import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  card: {
    maxWidth: 500,
  },
  fab: {
    marginLeft: theme.spacing(1.5),
    marginRight: theme.spacing(1),
  },
}));

export default function Tests() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const match = useParams();
  const [assignmentName, setAssignmentName] = useState('');
  const [tests, setTests] = useState([]);
  const [reset, setReset] = useState(0);
  const [warning, setWarning] = useState(null);

  React.useEffect(() => {
    axios.get(`/api/admin/assignments/get/${match?.assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.tests) {
        setTests(data?.tests ?? []);
      }
      if (data?.assignment?.name) {
        setAssignmentName(data?.assignment?.name ?? '');
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  const handleHide = (index, id, enqueueSnackbar) => () => {
    axios.get(`/api/admin/assignments/tests/toggle-hide/${id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (typeof data?.assignment_test?.hidden === 'boolean') {
        setTests((prev) => {
          prev[index].hidden = data?.assignment_test?.hidden;
          return [...prev];
        });
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const handleDelete = (index, id, enqueueSnackbar) => () => {
    setWarning(null);
    axios.get(`/api/admin/assignments/tests/delete/${id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (!!data) {
        setTests((prev) => {
          return [...prev.filter((item) => item.id !== id)];
        });
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  return (
    <div className={classes.root}>

      <Dialog
        open={!!warning}
        onClose={() => setWarning(null)}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{`Are you sure you wish to delete "${warning?.name}"?`}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            If you proceed with deleting the {`"${warning?.name}"`} test, any existing results
            will be lost forever.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setWarning(null)}
            color="primary"
            variant={'contained'}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDelete(warning?.index, warning?.id, enqueueSnackbar)}
            style={{backgroundColor: yellow[500]}}
            variant={'contained'}
            startIcon={<DeleteForeverIcon/>}
            autoFocus
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      <Grid container spacing={2} justifyContent={'center'} alignItems={'center'}>
        <Grid item xs={12}>
          <Typography variant="h6">
            Anubis
          </Typography>
          <Typography variant={'subtitle1'} color={'textSecondary'}>
            Assignment Tests Management
          </Typography>
        </Grid>
        <Grid item/>
        <Grid item xs={10}>
          <Grid container spacing={2}>
            {tests.map(({id, name, hidden}, index) => (
              <Grid item xs={12} md={6} key={`question-${index}`}>
                <Card>
                  <CardContent>
                    <Typography variant={'h6'}>
                      {name}
                    </Typography>
                    <FormControlLabel
                      checked={!hidden}
                      onChange={handleHide(index, id, enqueueSnackbar)}
                      control={<Switch color={'primary'}/>}
                      label={hidden ? 'hidden' : 'visible'}
                    />
                    <div/>
                    <FormControlLabel
                      onClick={() => setWarning({id, name, index})}
                      control={
                        <Tooltip title={'Delete test forever'}>
                          <Fab color={'secondary'} size={'small'} className={classes.fab}>
                            <DeleteForeverIcon/>
                          </Fab>
                        </Tooltip>
                      }
                      label={'delete test'}
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    </div>
  );
}
