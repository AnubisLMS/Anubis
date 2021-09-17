import createMuiTheme from '@material-ui/core/styles/createMuiTheme';
import FiraSans from '../fonts/FiraSans-Regular.ttf';


const fira = {
  fontFamily: 'FiraSans',
  fontStyle: 'normal',
  fontDisplay: 'swap',
  fontWeight: 400,
  src: `
    local('FiraSans'),
    local('FiraSans-Regular'),
    url(${FiraSans}) format('ttf')
  `,
  unicodeRange:
    'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, ' +
    'U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, ' +
    'U+2191, U+2193, U+2212, U+2215, U+FEFF',
};

let theme = createMuiTheme({
  palette: {
    primary: {
      main: '#5686F5',
    },
    dark: {
      black: '#0d1117',
      blue: {
        100: '#161b22',
        200: '#21262d',
      },
    },
    gray: {
      100: 'c6cdd5',
      200: '#89929b',
    },
    white: '#ecf2f8',
    color: {
      red: '#fa7970',
      orange: '#faa356',
      green: '#7ce38b',
      blue: '#77bdfb',
      purple: '#cea5fb',
    },
    type: 'dark',
  },
  typography: {
    fontFamily: 'FiraSans, Arial',
    h5: {
      fontWeight: 300,
      fontSize: 30,
      letterSpacing: 0.7,
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
  },
};

export default theme;
