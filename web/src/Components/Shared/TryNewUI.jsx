import React from 'react';
import Cookies from 'universal-cookie';
import Button from '@material-ui/core/Button';
import useMediaQuery from '@material-ui/core/useMediaQuery';
import {useTheme} from '@material-ui/core/styles';


export default function TryNewUI() {
  const cookies = new Cookies();
  const theme = useTheme();

  return (
    <div>
      <Button
        style={{
          position: 'fixed',
          right: 0,
          bottom: 0,
          marginBottom: 15,
          marginRight: 10,
          padding: 5,
          zIndex: 1,
        }}
        variant={'contained'}
        color={'primary'}
        onClick={() => {
          cookies.remove('web');
          setTimeout(() => {
            window.history.pushState('Anubis', 'Anubis', '/about');
            window.location.reload(0);
          }, 250);
        }}
      >
        Switch back to old UI
      </Button>
    </div>
  );
}
