import React, {useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import {DataGrid} from '@material-ui/data-grid';

const useStyles = makeStyles((theme) => ({
  paper: {
    minHeight: 700,
    width: '100%',
    padding: theme.spacing(1),
  },
}));

const CustomGrid = (
  {
    rows,
    columns,
    sortModel = {},
    onRowClick = () => {},
    onColumnClick = () => {},
    disableColumnMenu = false,
    loading = null,
  },
) => {
  const classes = useStyles();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(0);

  return (
    <Grid container spacing = {4}>
      <Grid item xs={12}>
        <Paper className = {classes.paper}>
          <div style = {{height: 700}}>
            <DataGrid
              pagination
              page = {page}
              rowsPerPageOptions={[10, 20, 30]}
              onPageChange={(value) => setPage(value.page)}
              onPageSizeChange={(value) => setPageSize(value.pageSize)}
              disableColumnMenu={disableColumnMenu}
              onRowClick={onRowClick}
              onColumnClick={onColumnClick}
              columns = {columns}
              rows = {rows}
              loading = {loading}

            />
          </div>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default CustomGrid;
