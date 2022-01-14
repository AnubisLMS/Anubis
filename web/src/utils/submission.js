export const translateSubmission = ({created, assignment_due, ...other}) => ({
  date_submitted: created.split(' ')[1], timestamp: new Date(created), time_submitted: created.split(' ')[0],
  assignment_due, on_time: new Date(created) <= new Date(assignment_due), created, ...other,
});
