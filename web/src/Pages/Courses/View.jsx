import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import CourseCard from "./Course";
import Grid from '@material-ui/core/Grid';
import Grow from "@material-ui/core/Grow";
//passes course data to individual course cards
const exampleCourses=  [
    {
    courseCode : "CS-UY 3224",
    courseName : "Intro to Operating Systems",
    instructor:"Gustavo Sandoval",
    section : "A",
    openAssignments: 2,
    totalAssignments: 5
    },
    {
        courseCode : "CS-UY 3943",
        courseName : "Intro to Offensive Security",
        instructor:"Bendan Dolan-Gavitt",
        section : "B",
        openAssignments: 0,
        totalAssignments: 6
        },
    {
        courseCode : "CS-UY 3224",
        courseName : "Intro to Operating Systems",
        instructor:"Gustavo Sandoval",
        section : "A",
        openAssignments: 2,
        totalAssignments: 5
        },
    {
        courseCode : "CS-UY 3943",
        courseName : "Intro to Offensive Security",
        instructor:"Bendan Dolan-Gavitt",
        section : "B",
        openAssignments: 0,
        totalAssignments: 6
        },
        
 ]
 const useStyles = makeStyles((theme) => ({
    control: {
      padding: theme.spacing(2),
    },
  }));



export default function CourseView(props){
   // const{courses} = props; maps to the request for current student courses.
   const classes = useStyles();
    return (       
        <Grid container   >
            <Grid item xs={12}>
                <Grid container justify="left" spacing={4}>
                    {exampleCourses.map((course,pos) =>(
                        <Grow
                        in={true}
                        style={{ transformOrigin: "0 0 0" }}
                        {...({ timeout: 300*(pos+1) })}
                        >
                            <Grid key={course.courseCode} item>
                                <CourseCard course={course}/>                                    
                            </Grid>
                        </Grow>
                        ))               
                    }                
                </Grid>
                
            </Grid>
        </Grid>       
    );
}