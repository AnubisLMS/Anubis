import React, {useEffect, useState} from 'react';
import Typography from '@mui/material/Typography';
import makeStyles from '@mui/styles/makeStyles';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-json';

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogTitle from '@mui/material/DialogTitle';
import Box from '@mui/material/Box';
import Checkbox from '@mui/material/Checkbox';

const useStyles = makeStyles((theme) => ({
  saveButton: {
    margin: theme.spacing(1),
  },
  root: {
    minWidth: 500,
  },
  markdown: {
    fontSize: '16px',
    margin: theme.spacing(1),
  },
  subTitle: {
    color: '#888888',
  },
  error: {
    marginLeft: theme.spacing(1),
    color: 'red',
  },
  actions: {
    justifyContent: 'space-between',
  },
  checkbox: {
    display: 'flex',
  },
}));

export default function BatchAddInput({isOpen, onAdd}) {
  const classes = useStyles();
  const [input, setInput] = useState('');
  const [error, setError] = useState(false);
  const [createPVC, setCreatePVC] = useState(false);

  useEffect(() => {
    if (input !== '') {
      try {
        JSON.parse(input);
      } catch (e) {
        setError('Invalid JSON');
        return;
      }
      setError(false);
    }
  }, [input]);

  return (
    <Box className={classes.root}>
      <Dialog
        open={isOpen}
      >
        <DialogTitle>Batch Add Students</DialogTitle>
        <Typography variant={'subtitle1'} className={classes.subTitle}>
          Your Answer:
        </Typography>

        <AceEditor
          theme="monokai"
          mode="json"
          onChange={setInput}
          value={input}
        />
        {error && (
          <Typography variant={'subtitle1'} className={classes.error}>
            {error}
          </Typography>
        )}
        <DialogActions className={classes.actions}>
          <Box className={classes.checkbox}>
            <Checkbox value={createPVC} onChange={(_, v) => setCreatePVC(v)}/>
            <p>
              Create PVC for each student
            </p>
          </Box>
          <Button
            variant="contained"
            color="primary"
            disabled={error}
            className={classes.saveButton}
            onClick={() => onAdd(JSON.parse(input), createPVC)}
          >
            Add Students
          </Button>
        </DialogActions>

      </Dialog>
    </Box>
  );
}
