import React, {useState} from 'react';
import ReactAce from 'react-ace';

import 'ace-builds/src-min-noconflict/theme-monokai';
import 'ace-builds/src-min-noconflict/mode-markdown';

import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import EditIcon from '@mui/icons-material/Edit';
import Box from '@mui/material/Box';
import SaveIcon from '@mui/icons-material/Save';


export default function DescriptionEditorDialog({assignment, updateField, saveAssignment, className}) {
  const [open, setOpen] = useState(false);
  const onClose = () => setOpen(false);
  return (
    <Box className={className}>
      <Button
        size={'small'}
        color={'primary'}
        variant={'contained'}
        startIcon={<EditIcon/>}
        onClick={() => setOpen(true)}
      >
        Edit Description
      </Button>
      {assignment && (
        <Dialog open={open} onClose={onClose}>
          <DialogTitle>
            Assignment Description
          </DialogTitle>
          <DialogContent>
            <ReactAce
              mode="markdown"
              theme="monokai"
              value={assignment.description}
              onChange={updateField(assignment.id, 'description', false, false, true)}
            />
          </DialogContent>
          <DialogActions>
            <Button
              variant={'contained'}
              color={'primary'}
              onClick={onClose}
            >
              Close
            </Button>
            <Button
              variant={'contained'}
              color={'primary'}
              onClick={() => {
                saveAssignment(assignment.id)();
                onClose();
              }}
              startIcon={<SaveIcon/>}
              autoFocus
            >
              Save
            </Button>
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
}

