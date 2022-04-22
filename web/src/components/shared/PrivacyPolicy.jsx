import React, {useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Modal from '@material-ui/core/Modal';
import Box from '@material-ui/core/Box';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';


const useStyles = makeStyles((theme) => ({
    root: {
        display: 'flex',
        backgroundColor: 'blue',
    },

}));


export default function PrivacyPolicy() {
    const classes = useStyles();
    const [open, setOpen] = useState(false);
    const handleOpen = () => setOpen(true);
    const handleClose = () => setOpen(false);
    return (
        <>
        <Button onClick={handleOpen}>Privacy Policy</Button>

        <Modal
        open={open}
        onClose={handleClose}
      >
        <Box className={classes.root}>
          <Typography variant="h6" component="h2">
          By using this application, you are agreeing to be bound by the terms and conditions of this agreement.
        If you do not agree to the terms of this agreement, do not use the application. This agreement is a legal document between you and the company
        and it governs your use of the application made available to you by the company. This agreement is between you
        and the company only and not with the application store. Therefore, the company is solely
        responsible for the application and its content. Although the application store is not a party to this
        agreement, it has the right to enforce it against you as a third party
        beneficiary relating to your use of the application. Since the application can be
        accessed and used by other users via, for example, family sharing/family group or volume purchasing, the use
        of the application by those users is expressly subject to this agreement. The application
        is licensed, not sold to you by the company for use strictly in accordance with the
        terms of this agreement.
          </Typography>
        </Box>
        </Modal>
        </>

    );
}
