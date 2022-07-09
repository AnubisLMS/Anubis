import {makeStyles} from '@mui/material/styles';
import {drawerWidth} from '../../../navconfig';

export const useStyles = makeStyles((theme) => ({
  drawer: {
    height: '100%',
    width: drawerWidth,
    flexShrink: 0,
    '& .MuiDrawer-paper::-webkit-scrollbar': {
      display: 'none',
    },
  },
  drawerPaper: {
    width: drawerWidth,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    paddingBottom: theme.spacing(4),
    backgroundColor: theme.palette.dark.blue['100'],
  },
  listContainer: {
    display: 'flex',
    flexDirection: 'column',
  },
  logoContainer: {
    padding: theme.spacing(4),
  },
  logo: {
    width: '100%',
  },
}));
