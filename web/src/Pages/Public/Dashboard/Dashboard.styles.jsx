import makeStyles from '@material-ui/core/styles/makeStyles';

export const useStyles = makeStyles((theme) => ({
  sectionContainer: {
    marginTop: '20px',
    padding: '40px',
    borderColor: '#21262D',
    border: '1px solid',
    borderRadius: '10px',
    width: '100%',
  },
  sectionHeader: {
    width: '100%',
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sectionHeaderTitle: {
    fontSize: '1.5rem',
  },
  sectionHeaderLink: {
    fontSize: '1rem',
    textDecoration: 'none',
    color: theme.palette.primary.main,
    '&:hover': {
      opacity: .8,
    },
  },
  sectionChildContainer: {
    paddingTop: '20px',
  },
  emptyContainer: {
    width: '100%',
    padding: theme.spacing(4),
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    border: `2px dashed ${theme.palette.dark.blue['200']}`,
  },
  emptyText: {
    fontSize: '16px',
    fontColor: theme.palette.dark.blue['200'],
    opacity: .7,
  },
  container: {
    paddingTop: theme.spacing(4),
  },
}));
