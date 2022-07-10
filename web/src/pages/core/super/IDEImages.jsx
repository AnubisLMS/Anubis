import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import {DataGrid} from '@mui/x-data-grid';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';

import SaveIcon from '@mui/icons-material/Save';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import makeStyles from '@mui/styles/makeStyles';


const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  paper: {
    padding: theme.spacing(1),
    height: 700,
  },
  button: {
    padding: theme.spacing(1),
  },
  tagsModel: {
    minWidth: 1024,
  },
}));


export default function IDEImages() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [tagsOpen, setTagsOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [images, setImages] = useState([]);

  const api = (method, url = `/api/super/ide/images/list`, config = {}) => {
    method(url, config).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.images) {
        setImages(data.images);
        if (!!tagsOpen) {
          for (const image of data.images) {
            if (image.id === tagsOpen.id) {
              setTagsOpen(image);
              break;
            }
          }
        }
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  useEffect(() => {
    api(axios.get);
  }, []);

  const addImage = () => {
    api(axios.post, `/api/super/ide/images/new`);
  };

  const addTag = (id) => {
    api(axios.post, `/api/super/ide/image-tags/new/${id}`);
  };

  const delTag = (id) => {
    api(axios.delete, `/api/super/ide/image-tags/delete/${id}`);
  };

  const saveImages = () => {
    api(axios.post, `/api/super/ide/images/save`, {images});
  };

  const updateImageOpen = (id, field, v) => {
    setEditOpen((prev) => {
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

  const updateTagOpen = (iid, id, field, v) => {
    setTagsOpen((prev) => {
      for (const tag of prev.tags) {
        if (tag.id === id) {
          tag[field] = v;
          break;
        }
      }
      return {...prev};
    });
    setImages((prev) => {
      for (const image of prev) {
        if (image.id === iid) {
          for (const tag of image.tags) {
            if (tag.id === id) {
              tag[field] = v;
              break;
            }
          }
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
      field: 'tags', width: 100, renderCell: (params) => (
        <Button
          startIcon={<EditIcon/>}
          variant={'contained'}
          color={'primary'}
          size={'small'}
          onClick={() => setTagsOpen(params.row)}
        >
          Tags
        </Button>
      ),
    },
    {
      field: 'edit', width: 100, renderCell: (params) => (
        <Button
          startIcon={<EditIcon/>}
          variant={'contained'}
          color={'primary'}
          size={'small'}
          onClick={() => setEditOpen(params.row)}
        >
          Edit
        </Button>
      ),
    },
  ];

  return (
    <div className={classes.root}>
      <Grid container spacing={4} justifyContent={'center'} alignItems={'center'}>
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
            open={!!editOpen}
            onClose={() => setEditOpen(false)}
          >
            <DialogTitle>Title</DialogTitle>
            <DialogContent>
              <Grid container spacing={2}>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    variant={'outlined'}
                    label={'Image'}
                    value={editOpen?.image}
                    onChange={(e) => updateImageOpen(editOpen?.id, 'image', e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    variant={'outlined'}
                    label={'Title'}
                    value={editOpen?.title}
                    onChange={(e) => updateImageOpen(editOpen?.id, 'title', e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    variant={'outlined'}
                    label={'Description'}
                    value={editOpen?.description}
                    onChange={(e) => updateImageOpen(editOpen?.id, 'description', e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    variant={'outlined'}
                    label={'Default Tag'}
                    value={editOpen?.default_tag}
                    onChange={(e) => updateImageOpen(editOpen?.id, 'default_tag', e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    variant={'outlined'}
                    label={'Icon'}
                    value={editOpen?.icon}
                    onChange={(e) => updateImageOpen(editOpen?.id, 'icon', e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <FormControlLabel
                    checked={!!editOpen?.webtop}
                    onChange={() => updateImageOpen(editOpen?.id, 'webtop', !editOpen?.webtop)}
                    labelPlacement={'end'}
                    control={<Switch color={'primary'}/>}
                    label={'webtop'}
                  />
                </Grid>

                <Grid item xs={12}>
                  <FormControlLabel
                    checked={!!editOpen?.public}
                    onChange={() => updateImageOpen(editOpen?.id, 'public', !editOpen?.public)}
                    labelPlacement={'end'}
                    control={<Switch color={'primary'}/>}
                    label={'public'}
                  />
                </Grid>

              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => {
                setEditOpen(false);
                saveImages();
              }} color="primary" variant="contained">
                Close
              </Button>
            </DialogActions>
          </Dialog>

          <Dialog
            open={!!tagsOpen}
            onClose={() => setTagsOpen(false)}
            maxWidth={'lg'}
          >
            <DialogTitle>Title</DialogTitle>
            <DialogContent className={classes.tagsModel}>
              {tagsOpen?.tags && (
                <Grid container spacing={2}>
                  {tagsOpen.tags.map((tag) => (
                    <Grid item xs={12} key={tag.id}>
                      <Grid container spacing={1}>
                        <Grid item xs>
                          <TextField
                            fullWidth
                            variant={'outlined'}
                            label={'Tag'}
                            value={tag.tag}
                            onChange={(e) => updateTagOpen(tagsOpen.id, tag.id, 'tag', e.target.value)}
                          />
                        </Grid>
                        <Grid item xs>
                          <TextField
                            fullWidth
                            variant={'outlined'}
                            label={'Title'}
                            value={tag.title}
                            onChange={(e) => updateTagOpen(tagsOpen.id, tag.id, 'title', e.target.value)}
                          />
                        </Grid>
                        <Grid item xs>
                          <TextField
                            fullWidth
                            variant={'outlined'}
                            label={'Description'}
                            value={tag.description}
                            onChange={(e) => updateTagOpen(tagsOpen.id, tag.id, 'description', e.target.value)}
                          />
                        </Grid>
                        <Grid item xs={1}>
                          <Button
                            startIcon={<DeleteForeverIcon/>}
                            color={'error'}
                            variant={'contained'}
                            className={classes.button}
                            onClick={() => delTag(tag.id)}
                          >
                            Delete
                          </Button>
                        </Grid>
                      </Grid>
                    </Grid>
                  ))}
                </Grid>
              )}
            </DialogContent>
            <DialogActions>
              <Button
                color={'primary'}
                variant={'contained'}
                startIcon={<AddIcon/>}
                onClick={() => {
                  addTag(tagsOpen?.id);
                }}
              >
                Add
              </Button>
              <Button
                color="primary"
                variant="contained"
                onClick={() => {
                  setTagsOpen(false);
                  saveImages();
                }}
              >
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

