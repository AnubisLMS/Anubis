import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import {DataGrid} from '@material-ui/data-grid/';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';

import SaveIcon from '@material-ui/icons/Save';
import EditIcon from '@material-ui/icons/Edit';
import AddIcon from '@material-ui/icons/Add';

import standardStatusHandler from '../../Utils/standardStatusHandler';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import makeStyles from '@material-ui/core/styles/makeStyles';


const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  paper: {
    padding: theme.spacing(1),
    height: 700,
  },
}));


export default function IDEImages() {
  const classes = useStyles();
  const [open, setOpen] = useState(false);
  const [images, setImages] = useState([]);
  const {enqueueSnackbar} = useSnackbar();

  const api = (method, url = `/api/super/ide/images/list`, config = {}) => {
    method(url, config).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.images) {
        setImages(data.images);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  useEffect(() => {
    api(axios.get);
  }, []);

  const addImage = () => {
    api(axios.post, `/api/super/ide/images/new`);
  };

  const saveImages = () => {
    api(axios.post, `/api/super/ide/images/save`, {images});
  };

  const updateOpen = (id, field, v) => {
    setOpen((prev) => {
      prev[field] = v;
      return {...prev};
    });
    setImages((prev) => {
      for (const image of prev) {
        if (image.id === id) {
          image[field] = v;
          break;
        }
      }
      return [...prev];
    });
  };

  const columns = [
    {field: 'image', width: 300},
    {field: 'title', width: 200},
    {field: 'public', width: 100},
    {
      field: 'edit', width: 100, renderCell: (params) => (
        <Button
          startIcon={<EditIcon/>}
          variant={'contained'}
          color={'primary'}
          size={'small'}
          onClick={() => setOpen(params.row)}
        >
          Edit
        </Button>
      ),
    },
  ];

  return (
    <div className={classes.root}>
      <Grid container spacing={4} justify={'center'} alignItems={'center'}>
        <Grid item xs={12}>
          <Typography variant="h6">
            Anubis
          </Typography>
          <Typography variant={'subtitle1'} color={'textSecondary'}>
            Config
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <Button
            variant={'contained'}
            color={'primary'}
            onClick={addImage}
            startIcon={<AddIcon/>}
          >
            Add Image
          </Button>
        </Grid>
        <Grid item xs={12}>
          <Button
            variant={'contained'}
            color={'primary'}
            onClick={saveImages}
            startIcon={<SaveIcon/>}
          >
            Save
          </Button>
        </Grid>
        <Grid item xs={12}>
          <Dialog
            open={!!open}
            onClose={() => setOpen(false)}
          >
            <DialogTitle>Title</DialogTitle>
            <DialogContent>
              <Grid container spacing={2}>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    variant={'outlined'}
                    label={'Image'}
                    value={open?.image}
                    onChange={(e) => updateOpen(open?.id, 'image', e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    variant={'outlined'}
                    label={'Title'}
                    value={open?.title}
                    onChange={(e) => updateOpen(open?.id, 'title', e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    variant={'outlined'}
                    label={'Description'}
                    value={open?.description}
                    onChange={(e) => updateOpen(open?.id, 'description', e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    variant={'outlined'}
                    label={'Icon'}
                    value={open?.icon}
                    onChange={(e) => updateOpen(open?.id, 'icon', e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <FormControlLabel
                    checked={!!open?.public}
                    onChange={() => updateOpen(open?.id, 'public', !open?.public)}
                    labelPlacement={'end'}
                    control={<Switch color={'primary'}/>}
                    label={'Public'}
                  />
                </Grid>

              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => {
                setOpen(false);
                saveImages();
              }} color="primary" variant="contained">
                Close
              </Button>
            </DialogActions>
          </Dialog>
          <Paper className={classes.paper}>
            <DataGrid
              rows={images}
              columns={columns}
              pageSize={10}
            />
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
}

