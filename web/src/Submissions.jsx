import React, {Fragment, useState} from 'react';
import Typography from '@material-ui/core/Typography';
import {makeStyles} from '@material-ui/core/styles';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import Divider from '@material-ui/core/Divider';
import {api} from './utils';
import {ListItemText} from "@material-ui/core";
import {Link,Redirect} from "react-router-dom";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import LinkIcon from "@material-ui/icons/Link";
import ListItemIcon from '@material-ui/core/ListItemIcon';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";
import InputAdornment from "@material-ui/core/InputAdornment";
import SearchIcon from '@material-ui/icons/Search';
import Grid from '@material-ui/core/Grid';

const useStyles = makeStyles(theme => ({
  paper: {
    maxWidth: 936,
    margin: 'auto',
    // overflow: 'hidden',
  },
  searchBar: {
    borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
  },
  searchInput: {
    fontSize: theme.typography.fontSize,
  },
  block: {
    display: 'block',
  },
  addUser: {
    marginRight: theme.spacing(1),
  },
  contentWrapper: {
    margin: '40px 16px',
  },
  toolbar: {
    backgroundColor: theme.palette.primary
  },
  card: {
    // minWidth: 275,
    margin: theme.spacing(2),
  },
  searchButton: {
    margin: theme.spacing(1)
  },
  searchbar: {
    justify: 'flex-end',
    alignItems: 'center',
  },
}));

function SearchSubmissions() {
  const classes = useStyles();
  const [commit, setCommit] = useState('');
  const [search, setSearch] = useState(false);

  if (search) {
    return <Redirect to={`/submissions/${commit.trim()}`}/>
  }

  return (
    <Card className={classes.card}>
      <CardContent>
        <Typography variant={'h6'} gutterBottom>
          Search for past submission
        </Typography>
        <Grid
          container
          direction={"row"}
          align={'center'}
          justify={'center'}
        >
          <Grid item xs={12} sm={10}>
            <TextField
              required
              autoFocus
              fullWidth
              variant={'outlined'}
              label={'commit hash'}
              InputProps={{
                startAdornment: <InputAdornment position="start"><SearchIcon/></InputAdornment>,
              }}
              onChange={e => setCommit(e.target.value)}
              onKeyPress={e => e.key === 'Enter' ? setSearch(true) : null}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button
              variant={"contained"}
              color={"primary"}
              className={classes.searchButton}
              onClick={() => setSearch(true)}
            >
              Search
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}

function RecentSubmissions({data}) {
  const classes = useStyles();
  return (
    <Card className={classes.card}>
      <CardContent>
        <Typography variant={'h6'}>
          Recent Submissions
        </Typography>
        <Typography variant={"body2"} color={"textSecondary"}>
          Last updated at: {data.timestamp}
        </Typography>
        <Typography variant={"body2"} color={"textSecondary"}>
          Updates every 30 seconds
        </Typography>
        <List>
          {data.success ? data.data.map(({timestamp, commit}) => (
            <Fragment key={commit}>
              <ListItem alignItems={"flex-start"}>
                <ListItemIcon>
                  <IconButton component={Link} to={`/submissions/${commit}`}>
                    <Tooltip title={'link'}>
                      <LinkIcon color={"primary"}/>
                    </Tooltip>
                  </IconButton>
                </ListItemIcon>
                <ListItemText
                  primary={
                    <React.Fragment>
                      <Typography
                        component={Link}
                        variant={"body2"}
                        className={classes.inline}
                        color={"textPrimary"}
                        to={`/submissions/${commit}`}
                      >
                        {commit}
                      </Typography>
                    </React.Fragment>
                  }
                  secondary={timestamp}
                >
                </ListItemText>
              </ListItem>
              <Divider variant="middle" color={"primary"}/>
            </Fragment>
          )) : null}
        </List>
      </CardContent>
    </Card>
  );
}

export default function Submissions() {
  const [data, setData] = useState([]);

  if (data.length === 0)
    api.get('/submissions').then(res => setData(res.data));

  if (!data || !data.success) return <div/>;

  return (
    <Fragment>
      <SearchSubmissions/>
      <RecentSubmissions data={data}/>
    </Fragment>
  );
}
