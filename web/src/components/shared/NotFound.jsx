import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import CardMedia from '@material-ui/core/CardMedia';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import RefreshIcon from '@material-ui/icons/Refresh';
import HomeIcon from '@material-ui/icons/Home';
import {Link} from 'react-router-dom';
import Tooltip from '@material-ui/core/Tooltip';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
    maxWidth: 345,
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    height: '100%',
  },
  expand: {
    transform: 'rotate(0deg)',
    transition: theme.transitions.create('transform', {
      duration: theme.transitions.duration.shortest,
    }),
  },
  expandOpen: {
    transform: 'rotate(180deg)',
  },
  media: {
    height: 0,
    // paddingTop: '56.25%', // 16:9
    paddingTop: '100%',
  },
  iconleft: {
    marginLeft: 'auto',
  },
}));

const quotes = [
  '"I\'ll have you know that I stubbed by toe last week and only cried for 20 minutes." – Spongebob',
  '"If you believe in yourself and with a tiny pinch of magic, all your dreams can come true." – Spongebob',
  '"Dumb people are always blissfully unaware of how dumb they really are…(drools)" – Patrick Star',
  '"Good people don’t rip other people’s arms off." – Spongebob',
  '"Can you give SpongeBob his brain back, I had to borrow it for the week." – Patrick Star',
  '"Excuse me, sir, but you’re sitting on my body, which is also my face." – Spongebob',
  '"The inner machinations of my mind are an enigma." – Patrick Star',
  '"Can I have everybody’s attention?… I have to use the bathroom." – Patrick',
];

function getQuote() {
  return quotes[Math.floor(Math.random() * quotes.length)];
}

export default function NotFound() {
  const classes = useStyles();
  const [quote, setQuote] = React.useState(getQuote());

  return (
    <Grid container alignItems={'center'} justify={'center'} direction={'column'}>
      <Grid item xs>
        <Card className={classes.root}>
          <CardHeader
            title={'Well that\'s a goof and a half...'}
            subheader={''}
          />
          <CardMedia
            className={classes.media}
            image={'/404.png'}
            title={'memes'}
          />
          <CardActions disableSpacing>
            <Tooltip title={'Mom come pick me up I\'m scared'}>
              <IconButton component={Link} to={'/'}>
                <HomeIcon/>
              </IconButton>
            </Tooltip>
            <Tooltip title={'Give me another darn SpongeBob quote!'}>
              <IconButton
                aria-label="reload quote"
                onClick={() => setQuote(getQuote())}
                className={classes.iconleft}
              >
                <RefreshIcon/>
              </IconButton>
            </Tooltip>
          </CardActions>
          <CardContent>
            <Typography paragraph>
              {quote}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
