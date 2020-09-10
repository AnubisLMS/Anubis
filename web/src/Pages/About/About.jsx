import React from "react";
import {makeStyles} from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";
import CardActionArea from '@material-ui/core/CardActionArea';
import CardContent from "@material-ui/core/CardContent";
import CardMedia from '@material-ui/core/CardMedia';
import Typography from "@material-ui/core/Typography";
import Grid from "@material-ui/core/Grid";

const useStyles = makeStyles({
  root: {
    maxWidth: 512,
  },
  authors: {}
});


export default function About() {
  const classes = useStyles();

  return (
    <Grid
      container
      direction="column"
      justify="center"
      alignItems="center"
      spacing={4}
    >
      {/* Jumbotron */}
      <Grid item xs={12}>
        <Card className={classes.root}>
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
                Anubis v2.0.0
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
                {"For inqueries: "}
                <a style={{color: "white"}} href={"mailto:anubis@osiris.cyber.nyu.edu"}>
                  anubis@osiris.cyber.nyu.edu
                </a>
              </Typography>
            </CardContent>
          </CardActionArea>
        </Card>
      </Grid>
      {/* END Jumbotron */}

      {/* Author section */}
      <Grid item xs={12}>
        <Card>
          <CardActionArea>
            <CardContent>
              <Typography gutterBottom variant="h5" component="h2">
                About the Authors
              </Typography>
              <Typography variant="body1" color="textSecondary" component="p">
                John Cunniff is a senior at NYU Tandon.
                Among his jobs and responsibilities he is
                the OSIRIS Cyber Security Research Lab President at NYU Tandon,
                the Chief Engineer at PlanetCurious,
                and the Head Infrastructure TA for Introduction to Operating Systems at NYU Tandon.
                John is a big fan of linux, Docker and Kubernetes.
              </Typography>
              <ul>
                <li><a style={{color: "white"}} href={"https://gitlab.com/juanpunchman"}>gitlab</a></li>
                <li><a style={{color: "white"}} href={"https://github.com/juan-punchman"}>github</a></li>
                <li><a style={{color: "white"}} href={"mailto:john@osiris.cyber.nyu.edu"}>contact</a></li>
              </ul>
              <br/><br/>
              <Typography variant="body1" color="textSecondary" component="p">
                Somto Ejinkonye is a Senior at NYU Tandon majoring in Computer Engineering with a minor
                in Cyber Security. Somto currently works as a Software Engineer for the Cyber Defense and Fraud Team at
                JPMorgan Chase, TA for Data Structures and Algorithms course
                and Infrastructure TA for the Introduction to Operating Systems course at NYU Tandon.
                Somto's intrests include embedded security, software engineering and electronics.
              </Typography>
              <ul>
                <li><a style={{color: "white"}} href={"https://github.com/Sejinkonye"}>github</a></li>
                <li><a style={{color: "white"}} href={"mailto:somto@osiris.cyber.nyu.edu"}>contact</a></li>
              </ul>
            </CardContent>
          </CardActionArea>
        </Card>
      </Grid>
      {/* END Author section */}

    </Grid>
  );
}
