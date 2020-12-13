import React from "react";
import {makeStyles, useTheme} from "@material-ui/core/styles";
import CircularProgress from "@material-ui/core/CircularProgress";
import {Redirect} from "react-router-dom";
import IconButton from "@material-ui/core/IconButton";
import LastPageIcon from "@material-ui/icons/LastPage";
import FirstPageIcon from "@material-ui/icons/FirstPage";
import KeyboardArrowRight from "@material-ui/icons/KeyboardArrowRight";
import KeyboardArrowLeft from "@material-ui/icons/KeyboardArrowLeft";
import PropTypes from "prop-types";
import TableContainer from "@material-ui/core/TableContainer";
import Paper from "@material-ui/core/Paper";
import Table from "@material-ui/core/Table";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import TableCell from "@material-ui/core/TableCell";
import TableBody from "@material-ui/core/TableBody";
import CheckCircleIcon from "@material-ui/icons/CheckCircle";
import green from "@material-ui/core/colors/green";
import red from "@material-ui/core/colors/red";
import blue from "@material-ui/core/colors/blue";
import grey from "@material-ui/core/colors/grey";
import CancelIcon from "@material-ui/icons/Cancel";
import TableFooter from "@material-ui/core/TableFooter";
import TablePagination from "@material-ui/core/TablePagination";
import ExitToAppOutlinedIcon from '@material-ui/icons/ExitToAppOutlined';
import CodeOutlinedIcon from "@material-ui/icons/CodeOutlined";
import DeleteForeverOutlinedIcon from '@material-ui/icons/DeleteForeverOutlined';
import useSubscribe from "../../useSubscribe";


const useStyles1 = makeStyles((theme) => ({
  root: {
    flexShrink: 0,
    marginLeft: theme.spacing(2.5),
  },
}));


const useStyles2 = makeStyles({
  root: {
    flexGrow: 1,
  },
  table: {
    minWidth: 500,
  },
  headerText: {
    fontWeight: 600
  },
  commitHashContainer: {

    width: 200,
    overflow: "hidden",
  }
});


function TablePaginationActions(props) {
  const classes = useStyles1();
  const theme = useTheme();
  const {count, page, rowsPerPage, onChangePage} = props;

  const handleFirstPageButtonClick = (event) => {
    onChangePage(event, 0);
  };

  const handleBackButtonClick = (event) => {
    onChangePage(event, page - 1);
  };

  const handleNextButtonClick = (event) => {
    onChangePage(event, page + 1);
  };

  const handleLastPageButtonClick = (event) => {
    onChangePage(event, Math.max(0, Math.ceil(count / rowsPerPage) - 1));
  };

  return (
    <div className={classes.root}>
      <IconButton
        onClick={handleFirstPageButtonClick}
        disabled={page === 0}
        aria-label="first page"
      >
        {theme.direction === 'rtl' ? <LastPageIcon/> : <FirstPageIcon/>}
      </IconButton>
      <IconButton onClick={handleBackButtonClick} disabled={page === 0} aria-label="previous page">
        {theme.direction === 'rtl' ? <KeyboardArrowRight/> : <KeyboardArrowLeft/>}
      </IconButton>
      <IconButton
        onClick={handleNextButtonClick}
        disabled={page >= Math.ceil(count / rowsPerPage) - 1}
        aria-label="next page"
      >
        {theme.direction === 'rtl' ? <KeyboardArrowLeft/> : <KeyboardArrowRight/>}
      </IconButton>
      <IconButton
        onClick={handleLastPageButtonClick}
        disabled={page >= Math.ceil(count / rowsPerPage) - 1}
        aria-label="last page"
      >
        {theme.direction === 'rtl' ? <FirstPageIcon/> : <LastPageIcon/>}
      </IconButton>
    </div>
  );
}


TablePaginationActions.propTypes = {
  count: PropTypes.number.isRequired,
  onChangePage: PropTypes.func.isRequired,
  page: PropTypes.number.isRequired,
  rowsPerPage: PropTypes.number.isRequired,
};


function IDETable({rows, headers}) {
  const classes = useStyles2()
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
            {headers.map(header => (
              <TableCell align="left">
                <b>{header}</b>
              </TableCell>
            ))}
          </TableRow>
        </TableHead>

        <TableBody>
          {(rowsPerPage > 0
              ? rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              : rows
          ).map(row => (
            <TableRow key={row.name} hover={true}
                      style={{textDecoration: 'none'}}>
              <TableCell>
                {row.state}
              </TableCell>
              <TableCell>
                {row.active
                  ? <CheckCircleIcon style={{color: green[500]}}/>
                  : <CancelIcon style={{color: red[500]}}/>}
              </TableCell>
              <TableCell>
                <IconButton component={"a"} href={`/api/public/ide/stop/${row.id}`} disabled={!row.active}>
                  <DeleteForeverOutlinedIcon style={{color: row.active ? red[500] : grey[500]}}/>
                </IconButton>
              </TableCell>
              <TableCell>
                {row.state === 'Initializing'
                  ? <CircularProgress/>
                  : <IconButton component={"a"} href={row.redirect_url} target="_blank" disabled={!row.active}>
                    <CodeOutlinedIcon style={{color: row.active ? blue[500] : grey[500]}}/>
                  </IconButton>
                }
              </TableCell>
              <TableCell>
                {row.assignment_name}
              </TableCell>
              <TableCell>
                {row.class_name}
              </TableCell>
              <TableCell>
                <IconButton component={"a"} href={row.repo_url} target="_blank">
                  <ExitToAppOutlinedIcon style={{color: blue[500]}}/>
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
  )
}

export default function IDE() {
  const {loading, error, data} = useSubscribe(
    '/api/public/ide/list',
    1000,
    _data => new Array(..._data.sessions).every(item => (
      item.state !== 'Initializing' && item.state !== 'Ending'
    )),
  );

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>

  return (
    <IDETable
      headers={[
        "Session State",
        "Session Active",
        "Stop Session",
        "Launch Session",
        "Assignment Name",
        "Class Name",
        "Assignment Repo",
        "Created",
      ]}
      rows={new Array(...data.sessions)}
    />
  );
}