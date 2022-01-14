import React, {useState, useRef} from 'react';
import {motion} from 'framer-motion';
import clsx from 'clsx';
import {useHistory} from 'react-router-dom';

import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import FiberManualRecordIcon from '@material-ui/icons/FiberManualRecord';

import {useStyles, useAnimations} from './SubmissionRow.styles';

const SubmissionRow = ({
  assignmentDue,
  assignment_name,
  commit,
  processed,
  tests,
  timeStamp,
}) => {
  const classes = useStyles();
  const variants = useAnimations();
  const history = useHistory();

  const [isOpen, setIsOpen] = useState(false);

  return (
    <Box
      className={classes.root}
      onClick={() => history.push(`/submission?commit=${commit}`)}
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      <Box display='flex' alignItems='center'>
        <Box marginRight='20px'>
          <FiberManualRecordIcon className={clsx(classes.circleIcon, processed ? classes.sucess : classes.error)}/>
        </Box>
        <Box
          className={classes.submissionTag}
          position='relative'
        >
          <Box
            className={classes.nameContainer}
            component={motion.div}
            animate={isOpen ? 'expanded' : 'closed'}
            variants={variants.nameContainer}
          >
            <Typography className={classes.assignmentName}>{assignment_name}</Typography>
          </Box>
          {isOpen &&
            <Box
              className={classes.commitContainer}
              component={motion.div}
              animate={isOpen ? 'expanded' : 'closed'}
              variants={variants.commitContainer}
            >
              <Typography className={classes.commit}>{commit.substring(0, 20)}</Typography>
            </Box>
          }
        </Box>
      </Box>
      <Typography className={classes.tests}>
        {`${tests.filter((test) => test.result.passed).length}/${tests.length} Tests Passed`}
      </Typography>
      <Typography
        className={clsx(classes.submittedStatus, timeStamp <= assignmentDue ? classes.sucess : classes.error)}
      >
        {timeStamp <= assignmentDue ? 'Submitted On Time' : 'Submitted Late'}
      </Typography>
      <Typography className={classes.submittedTime}>
        {new Date(timeStamp).toLocaleString()}
      </Typography>
    </Box>
  );
};

export default SubmissionRow;
