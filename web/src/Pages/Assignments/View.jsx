import React from "react";
import {makeStyles} from "@material-ui/core/styles";
import AssignmentCard from "./Assignment";
import Grid from '@material-ui/core/Grid';
import Grow from "@material-ui/core/Grow";
import useGet from "../../useGet";
import {useQuery} from "../../utils";
import CircularProgress from "@material-ui/core/CircularProgress";
import {Redirect} from "react-router-dom";
//passes assigment data 

// const exampleAssignments = [
//
//   {
//     courseCode: "CS-UY 3224",
//     assignmentNumber: "5",
//     assignmentId: "asdf",
//     assignmentTitle: "Extra Credit Bomblab",
//     dueDate: "9/2/20",
//     hasSubmission: false
//   },
//   {
//     courseCode: "CS-UY 3224",
//     assignmentNumber: "4",
//     assignmentId: "asdf",
//     assignmentTitle: "Memory",
//     dueDate: "8/31/20",
//     hasSubmission: false
//   },
//   {
//     courseCode: "CS-UY 3224",
//     assignmentNumber: "3",
//     assignmentId: "asdf",
//     assignmentTitle: "Scheduling",
//     dueDate: "8/8/20",
//     hasSubmission: true
//   },
//   {
//     courseCode: "CS-UY 3224",
//     assignmentNumber: "2",
//     assignmentId: "asdf",
//     assignmentTitle: "Assembly",
//     dueDate: "5/8/20",
//     hasSubmission: true
//   },
//   {
//     courseCode: "CS-UY 3224",
//     assignmentNumber: "1",
//     assignmentId: "asdf",
//     assignmentTitle: "Hello World & Uniq",
//     dueDate: "2/16/20",
//     hasSubmission: false
//   },
// ];

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

export default function AssignmentView(props) {
  const classes = useStyles();
  const query = useQuery();
  const {loading, error, data} = useGet(
    '/api/public/assignments',
    query.course ? {course: query.course} : {});

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  const translateAssignmentData = ({id, name, due_date, course, description, has_submission}, index) => ({
    courseCode: course.class_code, assignmentId: id, assignmentTitle: name, dueDate: due_date,
    hasSubmission: has_submission, assignmentDescription: description,
    assignmentNumber: data.assignments.length - index,
  });

  return (
    <Grid container>
      <Grid item xs={12}>
        <Grid container justify="left" spacing={4}>
          {data.assignments.map(translateAssignmentData).map((assignment, pos) => (
            <Grow
              key={assignment.assignmentId}
              in={true}
              style={{transformOrigin: "0 0 0"}}
              {...({timeout: 300 * (pos + 1)})}
            >
              <Grid item>
                {console.log(assignment) || null}
                <AssignmentCard assignment={assignment}/>
              </Grid>
            </Grow>
          ))}

        </Grid>
      </Grid>
    </Grid>
  );
}