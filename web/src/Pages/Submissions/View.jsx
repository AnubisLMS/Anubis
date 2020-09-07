import React from 'react';
import PropTypes from 'prop-types';
import {makeStyles, useTheme} from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableHead from '@material-ui/core/TableHead';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableFooter from '@material-ui/core/TableFooter';
import TablePagination from '@material-ui/core/TablePagination';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import IconButton from '@material-ui/core/IconButton';
import FirstPageIcon from '@material-ui/icons/FirstPage';
import KeyboardArrowLeft from '@material-ui/icons/KeyboardArrowLeft';
import KeyboardArrowRight from '@material-ui/icons/KeyboardArrowRight';
import LastPageIcon from '@material-ui/icons/LastPage';
import red from '@material-ui/core/colors/red';
import green from '@material-ui/core/colors/green';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import CancelIcon from '@material-ui/icons/Cancel';
import {Link, Redirect} from 'react-router-dom'
import CircularProgress from "@material-ui/core/CircularProgress";
import Grid from "@material-ui/core/Grid";
import Zoom from "@material-ui/core/Zoom";
import Typography from "@material-ui/core/Typography";
import useGet from '../../useGet'

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


export default function SubmissionsView() {
  const classes = useStyles2();
  const {loading, error, data} = useGet('/api/public/submissions')
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(10);

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>

  function translateSubmission({assignment_name, assignment_due, commit, processed, state, created}) {
    return {
      assignmentName: assignment_name, assignmentDue: new Date(assignment_due), state: state,
      commitHash: commit, processed: processed, timeSubmitted: created.split(' ')[0],
      dateSubmitted: created.split(' ')[1], timeStamp: new Date(created)};
  }

  const rows = data.submissions
    .map(translateSubmission)
    .sort((a, b) => (a.timeStamp > b.timeStamp ? -1 : 1)); //sorts submissions in reverse chronological order
  const emptyRows = rowsPerPage - Math.min(rowsPerPage, rows.length - page * rowsPerPage);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };


  return (
    <div className={classes.root}>
      <Grid container 
            direction="row" 
            justify="center" 
            alignItems="center"
            spacing={6}>
        <Grid item xs={12}>
          <Typography variant="h6">
            Submissions
          </Typography>
          <Typography variant="body1" className={classes.subtitle}>
            CS-UY 3224
          </Typography>
        </Grid>
        <Zoom in={true} timeout={200}>
          <Grid item xs>
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
                  {(rowsPerPage > 0
                      ? rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                      : rows
                  ).map((row, ind) => (
                    <TableRow key={row.name} hover={true}
                              component={Link}
                              style={{textDecoration: 'none'}}
                              to={`/courses/assignments/submissions/info?commit=${row.commitHash}`}>
                      <TableCell style={{width: 160}}>
                        {row.assignmentName}
                      </TableCell>
                      <TableCell style={{width: 160}}>
                        {row.commitHash}
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
          </Grid>
        </Zoom>
      </Grid>
    </div>
  );
}