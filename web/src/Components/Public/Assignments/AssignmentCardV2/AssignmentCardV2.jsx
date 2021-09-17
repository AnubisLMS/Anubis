import React from 'react';

import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import CardActionArea from '@material-ui/core/CardActionArea';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';

import {useStyles} from './AssignmentCardV2.styles';

const AssignmentCard = ({
  id,
  name,
  due_date,
  course,
}) => {
  const classes = useStyles();

  return (
    <div>

    </div>
  );
};

export default AssignmentCard;
