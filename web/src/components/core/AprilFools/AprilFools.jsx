import React from 'react';
import {makeStyles} from '@mui/material/styles';
import {Alert, AlertTitle} from '@mui/lab';
import IconButton from '@mui/material/IconButton';
import Collapse from '@mui/material/Collapse';
import CloseIcon from '@mui/icons-material/Close';
import Typography from '@mui/material/Typography';

const useStyles = makeStyles((theme) => ({
  root: {
    // position: 'fixed',
    zIndex: 3,
    width: '100%',
    '& > * + *': {
      marginTop: theme.spacing(2),
    },
  },
  a: {
    color: 'red',
  },
}));


export default function AprilFools() {
  const classes = useStyles();
  const [open, setOpen] = React.useState(true);

  return (
    <div className={classes.root}>
      <Collapse in={open}>
        <Alert severity="warning" action={
          <IconButton
            aria-label="close"
            color="inherit"
            size="medium"
            onClick={() => {
              setOpen(false);
            }}
          >
            <CloseIcon fontSize="inherit"/>
          </IconButton>
        }>
          <AlertTitle>Some changes are coming!</AlertTitle>
          <Typography variant={'h6'} gutterBottom>
            Soon there will be <strong><i>2 minute ad videos</i></strong> required when starting an IDE.
            Check out our
            {' '}<a className={classes.a} href="/api/public/memes/" rel="noreferrer" target="_blank">blog post</a>{' '}
            explaining the new and exciting changes to the platform
          </Typography>
        </Alert>
      </Collapse>
    </div>
  );
};
