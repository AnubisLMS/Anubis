import React from 'react';
import TableContainer from '@material-ui/core/TableContainer';
import Paper from '@material-ui/core/Paper';
import Table from '@material-ui/core/Table';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import TableBody from '@material-ui/core/TableBody';
import {Link} from 'react-router-dom';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import green from '@material-ui/core/colors/green';
import CancelIcon from '@material-ui/icons/Cancel';
import red from '@material-ui/core/colors/red';
import TableFooter from '@material-ui/core/TableFooter';
import TablePagination from '@material-ui/core/TablePagination';
import TablePaginationActions from '@material-ui/core/TablePagination/TablePaginationActions';
import {makeStyles} from '@material-ui/core/styles';

const useStyles = makeStyles({
  root: {
    flexGrow: 1,
  },
  table: {
    minWidth: 500,
  },
  headerText: {
    fontWeight: 600,
  },
  commitHashContainer: {

    width: 200,
    overflow: 'hidden',
  },
});

export function SubmissionsTable({rows}) {
  const classes = useStyles();
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(10);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const emptyRows = rowsPerPage - Math.min(rowsPerPage, rows.length - page * rowsPerPage);

  return (
    <TableContainer component={Paper}>
      <Table
        className={classes.table}
        aria-label="Submissions Table"
      >
        <TableHead>
          <TableRow>
            <TableCell align="left">
              <b>Assignment Name</b>
            </TableCell>
            <TableCell align="left">
              <b>Commit Hash</b>
            </TableCell>
            <TableCell align="center">
              <b>Processed</b>
            </TableCell>
            <TableCell align="left">
              <b>On Time</b>
            </TableCell>
            <TableCell align="left">
              <b>Date</b>
            </TableCell>
            <TableCell align="left">
              <b>Time</b>
            </TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {(rowsPerPage > 0 ?
              rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage) :
              rows
          ).map((row, ind) => (
            <TableRow key={row.name} hover={true}
              component={Link}
              style={{textDecoration: 'none'}}
              to={`/courses/assignments/submissions/info?commit=${row.commitHash}`}>
              <TableCell style={{width: 160}}>
                {row.assignmentName}
              </TableCell>
              <TableCell style={{width: 160}}>
                {row.commitHash.substring(0, 10)}
              </TableCell>
              <TableCell style={{width: 100}} align="center">
                {row.processed ? <CheckCircleIcon style={{color: green[500]}}/> :
                  <CancelIcon style={{color: red[500]}}/>}
              </TableCell>
              <TableCell style={{width: 120}} align="left">
                {row.timeStamp <= row.assignmentDue ? <CheckCircleIcon style={{color: green[500]}}/> :
                  <CancelIcon style={{color: red[500]}}/>}
              </TableCell>
              <TableCell style={{width: 100}} align="left">
                {row.timeSubmitted}
              </TableCell>
              <TableCell style={{width: 120}} align="left">
                {row.dateSubmitted}
              </TableCell>
            </TableRow>
          ))}

          {emptyRows > 0 && (
            <TableRow style={{height: 53 * emptyRows}}>
              <TableCell colSpan={6}/>
            </TableRow>
          )}
        </TableBody>
        <TableFooter>
          <TableRow>
            <TablePagination
              rowsPerPageOptions={[10, 20, 30, {label: 'All', value: -1}]}
              colSpan={4}
              count={rows.length}
              rowsPerPage={rowsPerPage}
              page={page}
              SelectProps={{
                inputProps: {'aria-label': 'rows per page'},
                native: true,
              }}
              onChangePage={handleChangePage}
              onChangeRowsPerPage={handleChangeRowsPerPage}
              ActionsComponent={TablePaginationActions}
              labelRowsPerPage="Submissions per page"
            />
          </TableRow>
        </TableFooter>
      </Table>
    </TableContainer>
  );
}
