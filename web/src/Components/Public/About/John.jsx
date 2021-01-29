import React from 'react';

import CardActionArea from '@material-ui/core/CardActionArea';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';

export default function John() {
  return (
    <Card>
      <CardActionArea>
        <CardContent>
          <Typography gutterBottom variant="h5" component="h2">
            John Cunniff
          </Typography>
          <Typography variant="body1" color="textSecondary" component="p">
            John Cunniff is a senior at NYU Tandon.
            Among his jobs and responsibilities he is
            the OSIRIS Cyber Security Research Lab President at NYU Tandon,
            the Chief Engineer at PlanetCurious,
            and the Head Infrastructure TA for Introduction to Operating Systems at NYU Tandon.
            John is a big fan of distributed computing.
          </Typography>
          <ul>
            <li><a style={{color: 'white'}} href={'https://gitlab.com/wabscale'}>gitlab</a></li>
            <li><a style={{color: 'white'}} href={'https://github.com/wabscale'}>github</a></li>
            <li><a style={{color: 'white'}} href={'mailto:john@osiris.cyber.nyu.edu'}>contact</a></li>
          </ul>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
