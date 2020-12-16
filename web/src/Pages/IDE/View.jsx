import React from "react";
import {makeStyles} from "@material-ui/core/styles";
import {Redirect} from "react-router-dom";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import Tooltip from "@material-ui/core/Tooltip";
import CircularProgress from "@material-ui/core/CircularProgress";
import CheckOutlinedIcon from '@material-ui/icons/CheckOutlined';
import CloseOutlinedIcon from '@material-ui/icons/CloseOutlined';
import IconButton from "@material-ui/core/IconButton";
import HelpOutlineOutlinedIcon from '@material-ui/icons/HelpOutlineOutlined';
import green from "@material-ui/core/colors/green";
import red from "@material-ui/core/colors/red";

import useSubscribe from "../../useSubscribe";
import IDETable from "./Table";
import Instructions from "./Instructions";


const useStyles = makeStyles((theme) => ({
  root: {
    flexShrink: 0,
    marginLeft: theme.spacing(2.5),
  },
  instructions: {
    paddingTop: theme.spacing(1),
    paddingLeft: theme.spacing(1),
  },
  available: {
    display: 'inline'
  }
}));


export default function IDE() {
  const classes = useStyles();
  const {loading, error, data} = useSubscribe(
    '/api/public/ide/list',
    1000,
    _data => new Array(..._data.sessions).every(item => (
      item.state !== 'Initializing' && item.state !== 'Ending'
    )),
  );

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>

  const {session_available} = data;

  return (
    <div className={classes.root}>
      <Grid container
            direction="row"
            justify="center"
            alignItems="center"
            spacing={6}>

        <Grid item xs={12}>
          <Typography variant="h6" className={classes.subtitle}>
            Anubis Cloud IDE
          </Typography>
          <Tooltip title={session_available ? "Anubis Cloud IDE Available" : "Anubis Cloud IDE Not Available"} className={classes.available}>
            <IconButton>
              {session_available
                ? <CheckOutlinedIcon style={{ color: green[500] }} fontSize={"large"}/>
                : <CloseOutlinedIcon style={{color: red[500]}} fontSize={"large"}/>}
            </IconButton>
          </Tooltip>
          <Typography variant={"body1"} className={classes.available}>
            {session_available
              ? "Anubis Cloud IDE session resources are currently available for use"
              : "Anubis Cloud IDE session resources are currently not available for use"}
          </Typography>
          <Tooltip title={session_available
            ? "Anubis Cloud IDE session resources are currently available for use. Go to the assignment " +
            "page to select which assignment you would like to launch an Anubis Cloud IDE for."
            : "The maximum quota of Anubis Cloud IDE sessions on our servers has been reached. " +
            "At this time, we cannot allocate more sessions until others have ended."}>
            <IconButton>
              <HelpOutlineOutlinedIcon fontSize={"small"}/>
            </IconButton>
          </Tooltip>
        </Grid>
        <Grid item xs={12}>
          <Instructions/>
        </Grid>

        <Grid item xs={12}>
          <IDETable
            headers={[
              "Session State",
              "Session Active",
              "End Session",
              "Launch Session",
              "Assignment Name",
              "Class Name",
              "Assignment Repo",
              "Created",
            ]}
            rows={new Array(...data.sessions)}
          />
        </Grid>
      </Grid>
    </div>
  );
}