import React, {useState, useEffect} from 'react';
import Typography from '@mui/material/Typography';
import makeStyles from '@mui/styles/makeStyles';
import AceEditor from 'react-ace';
import gfm from 'remark-gfm';
import ReactMarkdownWithHtml from 'react-markdown/with-html';

import 'ace-builds/src-min-noconflict/theme-monokai';
import 'ace-builds/src-min-noconflict/mode-c_cpp';
import 'ace-builds/src-min-noconflict/mode-python';
import 'ace-builds/src-min-noconflict/mode-markdown';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogTitle from '@mui/material/DialogTitle';
import Box from '@mui/material/Box';
import {DialogContent} from '@mui/material';
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
}));

export default function BatchAddInput({isOpen, onAdd}) {
  const classes = useStyles();
  const [input, setInput] = useState('');
  const [error, setError] = useState(false);
  const [createPVC, setCreatePVC] = useState(false);

  useEffect(() =>{
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
          onChange={setInput}
          value={input}
        />


        <DialogActions>
          {error && (
            <DialogContent>
              {error}
            </DialogContent>
          )}
          <Checkbox value={createPVC} onChange={setCreatePVC}/>
          <p>
            Create PVC for each student
          </p>

          <Button
            variant="contained"
            color="primary"
            disabled={error}
            className={classes.saveButton}
            onClick={() => onAdd({
              students: JSON.parse(input),
              create_pvc: createPVC,
            })}
          >
            Add Students
          </Button>
        </DialogActions>

      </Dialog>
    </Box>
  );
}
