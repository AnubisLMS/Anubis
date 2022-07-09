import React from 'react';
import {makeStyles} from '@mui/material/styles';
import CircularProgress from '@mui/material/CircularProgress';
import IconButton from '@mui/material/IconButton';
import TableContainer from '@mui/material/TableContainer';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import TableBody from '@mui/material/TableBody';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import green from '@mui/material/colors/green';
import red from '@mui/material/colors/red';
import blue from '@mui/material/colors/blue';
import grey from '@mui/material/colors/grey';
import CancelIcon from '@mui/icons-material/Cancel';
import TableFooter from '@mui/material/TableFooter';
import TablePagination from '@mui/material/TablePagination';
import CodeOutlinedIcon from '@mui/icons-material/CodeOutlined';
import DeleteForeverOutlinedIcon from '@mui/icons-material/DeleteForeverOutlined';
import TablePaginationActions from '@mui/material/TablePagination/TablePaginationActions';
import Tooltip from '@mui/material/Tooltip';
import GitHubIcon from '@mui/icons-material/GitHub';

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
