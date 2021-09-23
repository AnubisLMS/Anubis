import {makeStyles} from '@material-ui/core/styles';
import {drawerWidth} from '../../navconfig';

export const useStyles = makeStyles((theme) => ({
  drawer: {
    height: '100%',
    width: drawerWidth,
    flexShrink: 0,
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
