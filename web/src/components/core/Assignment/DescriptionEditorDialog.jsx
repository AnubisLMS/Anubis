import React, {useState} from 'react';
import ReactAce from 'react-ace';

import 'ace-builds/src-min-noconflict/theme-monokai';
import 'ace-builds/src-min-noconflict/mode-markdown';

import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import Button from '@material-ui/core/Button';
import EditIcon from '@material-ui/icons/Edit';
import Box from '@material-ui/core/Box';
import SaveIcon from '@material-ui/icons/Save';


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

