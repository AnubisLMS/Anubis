import React from "react";
import CourseCard from "./Course";
import Grid from '@material-ui/core/Grid';
import Grow from "@material-ui/core/Grow";
import useGet from '../../useGet';
import CircularProgress from '@material-ui/core/CircularProgress';
import {Redirect} from "react-router-dom";


//passes course data to individual course cards
// const exampleCourses = [
//   {
//     courseCode: "CS-UY 3224",
//     courseName: "Intro to Operating Systems",
//     instructor: "Gustavo Sandoval",
//     section: "A",
//     openAssignments: 2,
//     totalAssignments: 5
//   },
//   {
//     courseCode: "CS-UY 3943",
//     courseName: "Intro to Offensive Security",
//     instructor: "Bendan Dolan-Gavitt",
//     section: "B",
//     openAssignments: 0,
//     totalAssignments: 6
//   },
//   {
//     courseCode: "CS-UY 3224",
//     courseName: "Intro to Operating Systems",
//     instructor: "Gustavo Sandoval",
//     section: "A",
//     openAssignments: 2,
//     totalAssignments: 5
//   },
//   {
//     courseCode: "CS-UY 3943",
//     courseName: "Intro to Offensive Security",
//     instructor: "Bendan Dolan-Gavitt",
//     section: "B",
//     openAssignments: 0,
//     totalAssignments: 6
//   },
// ]


export default function CourseView() {
  // const{courses} = props; maps to the request for current student courses.
  const {loading, error, data} = useGet('/api/public/classes');

  if (loading) return <CircularProgress />;
  if (error) return <Redirect to={`/error`}/>

  const translateCourseData = ({name, class_code, section, professor, total_assignments, open_assignments}) => ({
    courseName: name, courseCode: class_code, section: section, instructor: professor,
    openAssignments: open_assignments, totalAssignments: total_assignments,
  });

  return (
    <Grid container>
      <Grid item xs={12}>
        <Grid container justify="left" spacing={4}>
          {data.classes.map(translateCourseData).map((course, pos) => (
            <Grow
              key={course.courseCode}
              in={true}
              style={{transformOrigin: "0 0 0"}}
              {...({timeout: 300 * (pos + 1)})}
            >
              <Grid item>
                <CourseCard course={course}/>
              </Grid>
            </Grow>
          ))}
        </Grid>

      </Grid>
    </Grid>
  );
}