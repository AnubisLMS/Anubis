import React from 'react';

import CardActionArea from '@material-ui/core/CardActionArea';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';

export default function Somto() {
  return (
    <Card>
      <CardActionArea>
        <CardContent>
          <Typography gutterBottom variant="h5" component="h2">
            Somto Ejinkonye
          </Typography>
          <Typography variant="body1" color="textSecondary" component="p">
            Somto Ejinkonye is a Senior at NYU Tandon majoring in Computer Engineering with a minor
            in Cyber Security. Somto currently works as a Software Engineer for the Cyber Defense and Fraud Team
            at JPMorgan Chase, TA for Data Structures and Algorithms course
            and Infrastructure TA for the Introduction to Operating Systems course at NYU Tandon.
            Somto&apos;s intrests include embedded security, software engineering and electronics.
          </Typography>
          <ul>
            <li><a style={{color: 'white'}} href={'https://github.com/Sejinkonye'}>github</a></li>
            <li><a style={{color: 'white'}} href={'mailto:somto@osiris.cyber.nyu.edu'}>contact</a></li>
          </ul>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
