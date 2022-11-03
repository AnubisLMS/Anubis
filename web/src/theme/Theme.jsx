import {createTheme} from '@mui/material/styles';
import FiraRegular from '../assets/fonts/FiraCode-Regular.ttf';

// Draft
const fira = {
  fontFamily: 'Fira Code',
  fontStyle: 'normal',
  fontDisplay: 'swap',
  fontWeight: 400,
  src: `
    local('Fira Code'),
    url(${FiraRegular}) format('ttf')
  `,
  unicodeRange:
    'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, ' +
    'U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, ' +
    'U+2191, U+2193, U+2212, U+2215, U+FEFF',
};
//

let theme = createTheme({
  palette: {
    primary: {
      main: '#5686F5',
    },
    secondary: {
      main: 'rgb(255, 152, 0)',
    },
    error: {
      main: 'rgb(244, 67, 54)',
    },
    dark: {
      black: '#0d1117',
      blue: {
        100: '#161b22',
        200: '#21262d',
      },
    },
    white: '#ecf2f8',
    color: {
      red: '#fa7970',
      orange: '#faa356',
      green: '#7ce38b',
      blue: '#77bdfb',
      purple: '#cea5fb',
      white: '#ecf2f8',
      gray: '#89929b',
    },
    mode: 'dark',
  },
  typography: {
    fontFamily: 'Fira Code',
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: `
        @font-face {
          font-family: 'Fira Code';
          font-style: normal; 
          font-display: swap;
          font-weight: 400;
          src: local('Fira Code'), url(${FiraRegular}) format('ttf');
          unicodeRange: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, 
          U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, 
          U+2191, U+2193, U+2212, U+2215, U+FEFF;
        }  
      `,
    },
  },
  shape: {
    borderRadius: 8,
  },
  props: {
    MuiTab: {
      disableRipple: true,
    },
  },
  mixins: {
    toolbar: {
      minHeight: 48,

    },
  },
});

theme = {
  ...theme,
  overrides: {
    MuiButton: {
      label: {
        textTransform: 'none',
      },
    },
    MuiDialog: {
      paper: {
        backgroundColor: theme.palette.dark.blue['200'],
        padding: '20px',
      },
    },
    MuiPaper: {
      root: {
        backgroundColor: theme.palette.dark.blue['200'],
      },
    },
    MuiDataGrid: {
      root: {
        backgroundColor: theme.palette.dark.blue['100'],
        borderColor: theme.palette.primary.main,
      },
    },
    MuiCssBaseline: {
      '@global': {
        '@font-face': fira,
      },
    },
  },
};

export default theme;
