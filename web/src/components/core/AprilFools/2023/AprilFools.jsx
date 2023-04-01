import React from 'react';
import Collapse from '@mui/material/Collapse';
import Grid from '@mui/material/Grid';
import {styled, useTheme} from '@mui/material/styles';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import './rainbow.css';

const Item = ({children, close, p = 4, ...extra}) => {
  const theme = useTheme();
  return (
    <Paper sx={{
      backgroundColor: '#fafbfc',
      borderColor: '#d3d4d7',
      borderWidth: '4px',
      padding: theme.spacing(1),
      textAlign: 'center',
      // color: theme.palette.text.secondary,
    }} variant={'outlined'}>
      <Button sx={{
        ...extra,
        p: p,
        color: '#3399cc',
        fontSize: '36px',
        height: '100%',
        width: '100%',
      }} onClick={close}>
        {children}
      </Button>
    </Paper>
  );
};

styled(Paper)(({theme}) => ({}));
export default function AprilFools() {
  const [open, setOpen] = React.useState(true);
  const close = () => setOpen(false);
  const theme=useTheme();

  return (
    <React.Fragment>
      <Collapse in={!open}>
        <Paper sx={{
          p: 2, mt: 2, mb: 2,
          backgroundColor: theme.palette.dark.blue['100'],
          border: `1px solid ${theme.palette.dark.blue['200']}`}}
        >
          <Grid container spacing={2} justifyContent={'space-between'} alignItems={'center'}>
            <Grid item>
              April Fools!
            </Grid>
            <Grid item>
              <Button variant={'contained'} color={'primary'} onClick={() => setOpen(true)}>
                See again
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Collapse>
      <Collapse in={open}>
        <Paper
          sx={{
            backgroundColor: '#f1f3f4',
            mb: 1, bt: 1, p: 4,
          }}
          square
        >
          <Grid container spacing={2} direction={'row'} justifyContent={'center'} alignItems={'center'}>
            <Grid item xs={12} md={8} xl={4}>
              <Grid container spacing={2} justifyContent={'center'} alignItems={'center'}>
                <Grid item xs={12} md={6}>
                  <img src={'/aprilfools/200w.gif'}/>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box sx={{p: 1, color: '#000', textAlign: 'center'}} class="rainbow rainbow_text_animated">
                  Buy one Anubis NFT to open an IDE!
                  </Box>
                </Grid>
              </Grid>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{
                backgroundColor: '#fafbfc',
                borderColor: '#d3d4d7',
                borderWidth: '4px',
                mt: 2, mb: 2, p: 4,
                flexGrow: 1,
              }} variant={'outlined'}>
                <Grid container spacing={2}>

                  {/* % tip grid */}
                  <Grid item xs={3} md={4}>
                    <Item close={close}>$10</Item>
                  </Grid>
                  <Grid item xs={3} md={4}>
                    <Item close={close}>$20</Item>
                  </Grid>
                  <Grid item xs={3} md={4}>
                    <Item close={close}>$30</Item>
                  </Grid>

                  {/* Custom Tip */}
                  <Grid item xs={12} md={12}>
                    <Item close={close} pt={4} pb={4}>Custom Amount</Item>
                  </Grid>

                  {/* No Tip */}
                  <Grid item xs={12} md={12}>
                    <Item close={close} pt={4} pb={4}>Skip</Item>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        </Paper>
      </Collapse>
    </React.Fragment>
  );
};
