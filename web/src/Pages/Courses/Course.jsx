import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import {Redirect, Link} from "react-router-dom";

import Card from "@material-ui/core/Card";
import CardActionArea from '@material-ui/core/CardActionArea';
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import Badge from '@material-ui/core/Badge';

//course is visually represented by a card

const useStyles = makeStyles({
  root: {
    flexGrow: 1,
 
    minWidth: 275,
    maxWidth: 280
  },
  bullet: {
    display: "inline-block",
    margin: "0 2px",
    transform: "scale(0.8)"
  },
  sem: {
    fontSize: 14,
  
  },
  pos: {
    marginBottom: 12
  },
  title: {
   marginTop: 10
  }
});


export default function CourseCard(props) {
  const {courseCode, courseName, instructor, section, openAssignments, totalAssignments } = props.course;
  //will have notification to indicate number of open assignment with no submissions
  const classes = useStyles();
  const bull = <span className={classes.bullet}>•</span>;
  const handleClick =(event)=>{
  }

  return (
    <Badge badgeContent={openAssignments} color="error" fontSize="medium" >

    <Card className={classes.root} >     
       
      <CardActionArea 
        component={Link} 
        to={`/courses/${courseCode.replace(/\s+/g,'')}/assignments`} > 
        
        <CardContent>
          <Typography 
            className={classes.sem}
            color="textSecondary"
            gutterBottom
          >
            Fall 2020
          </Typography>
         
          <Typography className={classes.title} variant="h6" component="h2">
            {courseName}   
          </Typography>
          <Typography className={classes.pos} color="textSecondary">
          {courseCode} {bull} {section}
          </Typography>
          <Typography variant="body2" component="p">
           {instructor} 
          </Typography>
        </CardContent>          
        <CardActions>          
        <Button size="small" color="primary">
          {`${totalAssignments} Assigments`}
        </Button>        
      </CardActions>  
     
      </CardActionArea> 
        
    </Card>
    </Badge>
  );
}
