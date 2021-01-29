import React from 'react';

import CardActionArea from '@material-ui/core/CardActionArea';
import CardMedia from '@material-ui/core/CardMedia';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';

export default function Description(props) {
  return (
    <Card {...props}>
      <CardActionArea>
        <CardMedia
          component="img"
          alt="anubis logo"
          height="512"
          width="512"
          image="/logo512.png"
        />
        <CardContent>
          <Typography gutterBottom variant="h5" component="h2">
            Anubis v2.2.0
          </Typography>
          <Typography variant="body1" color="textSecondary" component="p">
            Anubis is a custom built, distributed autograder created by John Cunniff, and Somto Ejinkonye.
            It acts as a massive
            cd/ci for homework repos. Each student uses github classroom to get their own private repo
            for each assignment. When they push to the repo and therefore submit, we run basic pass
            fail tests on that submission. Students can then view their submission and the status of their
            results on this website. New in v2.0.0, submission results are viewable live. This means
            students can watch their submission results come in as they are processed.
          </Typography>
          <br/>
          <Typography variant="body1" color="textSecondary" component="p">
            {'For inqueries: '}
            <a style={{color: 'white'}} href={'mailto:anubis@osiris.cyber.nyu.edu'}>
              anubis@osiris.cyber.nyu.edu
            </a>
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
