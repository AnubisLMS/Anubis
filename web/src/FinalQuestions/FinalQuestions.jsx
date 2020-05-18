import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import List from "@material-ui/core/List";
import React from "react";
import {makeStyles} from "@material-ui/core/styles";
import {green} from "@material-ui/core/colors";

const useStyles = makeStyles(theme => ({
  paper: {
    maxWidth: 936,
    margin: theme.spacing(2),
    padding: theme.spacing(2),
    overflow: 'hidden',
  },
  searchBar: {
    borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
  },
  searchInput: {
    fontSize: theme.typography.fontSize,
  },
  title: {
    fontSize: 14,
  },
  block: {
    display: 'block',
  },
  addUser: {
    marginRight: theme.spacing(1),
  },
  contentWrapper: {
    margin: '40px 16px',
  },
  card: {
    minWidth: 275,
  },
  list: {
    width: '100%',
  },
  dialog: {
    margin: theme.spacing(2),
    padding: theme.spacing(2)
  },
  closeButton: {
    position: 'absolute',
    right: theme.spacing(1),
    top: theme.spacing(1),
    color: theme.palette.grey[500],
  },
  progress: {
    padding: theme.spacing(1)
  },
  fabProgress: {
    color: green[500],
    position: 'absolute',
    top: -6,
    left: -6,
    zIndex: 1,
  },
  buttonProgress: {
    color: green[500],
    position: 'absolute',
    top: '50%',
    left: '50%',
    marginTop: -12,
    marginLeft: -12,
  },
  wrapper: {
    margin: theme.spacing(1),
    position: 'relative',
  },
}));

export default function FinalQuestions({data}) {
  const classes = useStyles();
  if (!data) return <div/>;
  const {questions, student} = data;

  return (
    <Card className={classes.card}>
      <CardContent>
        <Typography variant={'h6'} component={'h2'}>
          {`${student.netid}'s questions`}
        </Typography>
        <List>
        </List>
      </CardContent>
    </Card>
  );
}