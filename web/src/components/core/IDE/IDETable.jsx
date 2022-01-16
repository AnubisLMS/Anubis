import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import IconButton from '@material-ui/core/IconButton';
import TableContainer from '@material-ui/core/TableContainer';
import Paper from '@material-ui/core/Paper';
import Table from '@material-ui/core/Table';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import TableBody from '@material-ui/core/TableBody';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import green from '@material-ui/core/colors/green';
import red from '@material-ui/core/colors/red';
import blue from '@material-ui/core/colors/blue';
import grey from '@material-ui/core/colors/grey';
import CancelIcon from '@material-ui/icons/Cancel';
import TableFooter from '@material-ui/core/TableFooter';
import TablePagination from '@material-ui/core/TablePagination';
import CodeOutlinedIcon from '@material-ui/icons/CodeOutlined';
import DeleteForeverOutlinedIcon from '@material-ui/icons/DeleteForeverOutlined';
import TablePaginationActions from '@material-ui/core/TablePagination/TablePaginationActions';
import Tooltip from '@material-ui/core/Tooltip';
import GitHubIcon from '@material-ui/icons/GitHub';

const useStyles = makeStyles({
  table: {
    minWidth: 500,
  },
});

const header = [
  'Session State',
  'Session Active',
  'End Session',
  'Launch Session',
  'Assignment Name',
  'Class Name',
  'Assignment Repo',
  'Created',
];

export default function IDETable({rows}) {
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
            {header.map((header) => (
              <TableCell key={`header-${header}`} align="left">
                <b>{header}</b>
              </TableCell>
            ))}
          </TableRow>
        </TableHead>

        <TableBody>
          {(rowsPerPage > 0 ?
            rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage) :
            rows
          ).map((row) => (
            <TableRow key={row.name} hover={true}
              style={{textDecoration: 'none'}}>
              <TableCell>
                {row.state}
              </TableCell>
              <TableCell>
                {row.active ?
                  <CheckCircleIcon style={{color: green[500]}}/> :
                  <CancelIcon style={{color: red[500]}}/>}
              </TableCell>
              <TableCell>
                <Tooltip title={'End IDE Session'}>
                  <IconButton component={'a'} href={`/api/public/ide/stop/${row.id}`} disabled={!row.active}>
                    <DeleteForeverOutlinedIcon style={{color: row.active ? red[500] : grey[500]}}/>
                  </IconButton>
                </Tooltip>
              </TableCell>
              <TableCell>
                {row.state === 'Initializing' ?
                  <CircularProgress/> :
                  <Tooltip title={'Open Cloud IDE Session'}>
                    <IconButton component={'a'} href={row.redirect_url} target="_blank" disabled={!row.active}>
                      <CodeOutlinedIcon style={{color: row.active ? blue[500] : grey[500]}}/>
                    </IconButton>
                  </Tooltip>
                }
              </TableCell>
              <TableCell>
                {row.assignment_name}
              </TableCell>
              <TableCell>
                {row.class_name}
              </TableCell>
              <TableCell>
                <IconButton component={'a'} href={row.repo_url} target="_blank">
                  <GitHubIcon style={{color: blue[500]}}/>
                </IconButton>
              </TableCell>
              <TableCell>
                {row.created}
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
