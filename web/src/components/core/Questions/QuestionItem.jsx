import React from 'react';

import AssessmentIcon from '@material-ui/icons/Assessment';
import Typography from '@material-ui/core/Typography';
import red from '@material-ui/core/colors/red';
import orange from '@material-ui/core/colors/orange';
import green from '@material-ui/core/colors/green';
import useTheme from '@material-ui/core/styles/useTheme';

import Item from '../../shared/Item/Item';

export default function QuestionItem({question, onClick}) {
  const theme = useTheme();
  const {submitted, late} = question?.response ?? {};
  let status;
  let statusColor;
  let statusColorCss;

  if (submitted) {
    if (!late) {
      status = `Submitted On Time`;
      statusColor = 'green';
      statusColorCss = theme.palette.color.green;
    } else {
      status = `Submitted Late`;
      statusColor = 'orange';
      statusColorCss = theme.palette.color.orange;
    }
  } else {
    status = 'No Submission';
    statusColor = 'red';
    statusColorCss = theme.palette.color.orange;
  }

  return (
    <Item
      showStatus={true}
      statusColor={statusColor}
      title={`Question ${question?.question?.pool ?? ''}`}
      subTitle={submitted ? `Last modified ${submitted}` : status}
      titleIcon={<AssessmentIcon/>}
      onClick={onClick}
    >
      <Typography style={{color: statusColorCss}}>
        {status}
      </Typography>
      <Typography> {!!submitted ? new Date(submitted).toLocaleString() : 'No Submission'}</Typography>
    </Item>
  );
};
