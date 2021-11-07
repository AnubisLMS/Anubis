import React, {useState} from 'react';
import {motion} from 'framer-motion';
import clsx from 'clsx';
import {useHistory} from 'react-router-dom';

import Box from '@material-ui/core/Box';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import ListItemIcon from '@material-ui/core/ListItemIcon';

import {useStyles, useAnimations} from './Item.styles.jsx';
import FiberManualRecordIcon from '@material-ui/icons/FiberManualRecord';


const Item = ({
  showStatus,
  statusColor,
  titleIcon,
  title,
  subTitle,
  link,
  children,
}) => {
  const classes = useStyles();
  const variants = useAnimations();
  const history = useHistory();

  const [isSelected, setIsSelected] = useState(false);

  const blockSize = 12/(children?.length + 1);

  return (
    <Box
      className={classes.root}
      onClick={() => history.push(link)}
      onMouseEnter={() => setIsSelected(true)}
      onMouseLeave={() => setIsSelected(false)}
    >
      <Grid
        container
        position='relative'
      >
        <Grid Item xs={blockSize} justifyContent='flex-start' className={classes.block}>
          {showStatus && statusColor && (
            <Box marginRight='20px'>
              <FiberManualRecordIcon className={clsx(
                classes.statusIcon, statusColor === 'red' ? classes.red : statusColor === 'orange' ? classes.orange :
                  statusColor === 'green' ? classes.green : classes.blue)
              }/>
            </Box>
          )}
          <Box className={classes.titleIconContainer}>
            {titleIcon}
          </Box>
          <Box>
            <Box
              className={classes.titleContainer}
              component={motion.div}
              animate={isSelected ? 'expanded' : 'closed'}
              variants={variants.nameContainer}
            >
              <Typography className={classes.title}>{title}</Typography>
            </Box>
            {isSelected &&
            <Box
              className={classes.subTitleContainer}
              component={motion.div}
              animate={isSelected ? 'expanded' : 'closed'}
              variants={variants.commitContainer}
            >
              <Typography className={classes.subTitle}>{subTitle}</Typography>
            </Box>
            }
          </Box>
        </Grid>
        {children && children.map((child, index) => (
          <Grid
            item
            xs={blockSize}
            key={index}
            className={clsx(classes.block, index === children.length - 1 ? classes.end : classes.center)}
          >
            {child}
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default Item;
