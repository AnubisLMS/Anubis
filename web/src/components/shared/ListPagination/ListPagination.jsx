import React from 'react';
import {useStyles} from './ListPagination.styles';
import clsx from 'clsx';

import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';

import Button from '@mui/material/Button';

const ListPagination = ({
  page,
  nextPage,
  prevPage,
  maxPage,
  setPage,
}) => {
  const classes = useStyles();
  return (
    <div className={classes.root}>
      <div className={classes.paginate}>
        <Button onClick={prevPage}> <ArrowBackIosIcon /> </Button>
        {page > 0 && (
          <Button
            onClick={() => setPage(page - 1 )}
            className={classes.page}>{page}</Button>
        )}
        <Button className={classes.active}>{page + 1}</Button>
        {page >= 0 && page <= maxPage -2 && (
          <Button
            onClick={() => setPage(page + 1)}
            className={classes.page}>{page + 2}</Button>
        )}
        <Button onClick={nextPage}> <ArrowForwardIosIcon /> </Button>
      </div>
    </div>
  );
};

export default ListPagination;

