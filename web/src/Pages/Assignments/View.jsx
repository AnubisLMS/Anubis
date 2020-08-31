import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import AssignmentCard from "./Assignment";
import Grid from '@material-ui/core/Grid';
import Grow from "@material-ui/core/Grow";
//passes assigment data 

const exampleAssignments = [

    {
        courseCode:"CS-UY 3224",
        assignmentNumber:"5",
        assignmentId:"asdf",
        assignmentTitle:"Extra Credit Bomblab",
        dueDate:"9/2/20",
        hasSubmission: false
    },
    {
        courseCode:"CS-UY 3224",
        assignmentNumber:"4",
        assignmentId:"asdf",
        assignmentTitle:"Memory",
        dueDate:"8/31/20",
        hasSubmission: false
    },
    {
        courseCode:"CS-UY 3224",
        assignmentNumber:"3",
        assignmentId:"asdf",
        assignmentTitle:"Scheduling",
        dueDate:"8/8/20",
        hasSubmission: true
    },
    {
        courseCode:"CS-UY 3224",
        assignmentNumber:"2",
        assignmentId:"asdf",
        assignmentTitle:"Assembly",
        dueDate:"5/8/20",
        hasSubmission: true
    },
    {
        courseCode:"CS-UY 3224",
        assignmentNumber:"1",
        assignmentId:"asdf",
        assignmentTitle:"Hello World & Uniq",
        dueDate:"2/16/20",
        hasSubmission: false
    },
];

const useStyles = makeStyles((theme) => ({
    control: {
        padding: theme.spacing(2),
      },
    container: {
    display: 'flex',
    },
    paper: {
        margin: theme.spacing(1),
      },
}));

export default function AssignmentView(props){

    const classes = useStyles();
    return(
        <Grid container  >

            <Grid item xs={12}>
                <Grid container justify="left" spacing={4}>                
                    {exampleAssignments.map((assignment, pos) =>(
                        <Grow
                        in={true}
                        style={{ transformOrigin: "0 0 0" }}
                        {...({ timeout: 300*(pos+1) })}
                        >
                            <Grid key={assignment.assignmentId} item>
                                <AssignmentCard assignment={assignment}/>
                            </Grid>
                        </Grow>
                    ))}

                </Grid>
            </Grid>
        </Grid>  
    );
}