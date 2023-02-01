import React from 'react';

import AceEditor from 'react-ace';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import DialogActions from '@mui/material/DialogActions';
import FormHelperText from '@mui/material/FormHelperText';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import DialogTitle from '@mui/material/DialogTitle';
import 'ace-builds/src-min-noconflict/theme-monokai';
import 'ace-builds/src-min-noconflict/mode-sh';

import useAdmin from '../../../hooks/useAdmin';
import downloadTextFile from '../../../utils/downloadTextFile';

export default function RepoCommandDialog({repos = [], assignment = {}}) {
  const [open, setOpen] = React.useState(false);
  const [http, setHttp] = React.useState(false);
  const [verbose, setVerbose] = React.useState(false);
  // We assume that the group is unset when group=-1
  const [group, setGroup] = React.useState(-1);
  const tas = useAdmin('ta');
  const professors = useAdmin('professor');
  const students = useAdmin('student');

  const filteredRepos = React.useMemo(()=>{
    const superusers = students.filter((student)=>student.is_superuser);
    const admins = tas.concat(professors).concat(superusers);
    const adminNetids = new Set(admins.map((item) => item.netid));

    let filteredRepos = repos.map((repo) => ({
      ownedByAdmin: adminNetids.has(repo.netid),
      ...repo,
    }));
    filteredRepos.sort((a, b) => (a.name < b.name) ? -1 : 1);
    if (group >= 0) {
      filteredRepos = filteredRepos.filter((repo) => !repo.ownedByAdmin);
      const workloadPerTA = Math.ceil(filteredRepos.length / tas.length);
      const start = workloadPerTA * group;
      filteredRepos = filteredRepos.slice(start, start + workloadPerTA);
    }
    return filteredRepos;
  }, [tas, professors, students, repos, group]);

  const script = React.useMemo(()=>{
    if (assignment.name === undefined) {
      return '';
    }
    const assignmentDir = assignment.name.replaceAll(' ', '_');
    const repoDir = (netid, name) => netid + (verbose ? `_${name?.replaceAll(' ', '_')}` : '');
    const ownerInfoCmd = `echo '${filteredRepos.map((repo)=>`${repo.netid} ${repo.name}`).join('\\n')}' > students\n`;
    const cloneCmds = filteredRepos.map(({url, ssh, netid, name}) =>
      `git clone '${http ? url : ssh}' '${repoDir(netid, name)}'`).join('\n');
    return `mkdir -p '${assignmentDir}'\n` +
      `cd '${assignmentDir}'\n` +
      (verbose ? ownerInfoCmd : '') +
      cloneCmds;
  }, [http, assignment, filteredRepos, verbose]);

  const handleClickOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  return (
    <div>
      <Button variant="contained" color="primary" onClick={handleClickOpen}>
        View Clone Command
      </Button>
      <Dialog open={open} onClose={handleClose} fullWidth>
        <DialogTitle>View Clone Command</DialogTitle>
        <DialogContent>
          <FormGroup>
            <InputLabel label="group-select">Grading Groups</InputLabel>
            <Select fullWidth name="group-select" onChange={(e)=>setGroup(e.target.value)} value={group}>
              <MenuItem value={-1}>All Users</MenuItem>
              {tas.map((_, index) => (
                <MenuItem value={index} key={index}>Group {index+1}</MenuItem>
              ))}
            </Select>
            <FormControlLabel
              control={
                <Switch
                  checked={http}
                  onChange={() => setHttp(!http)}
                  name="http"
                  color="primary"
                />
              }
              label={http ? 'http' : 'ssh'}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={verbose}
                  onChange={() => setVerbose(!verbose)}
                  name="verbose"
                  color="primary"
                />
              }
              label={verbose ? 'verbose' : 'basic'}
            />
            <FormHelperText>
              Switch on to output student names to a file and name cloned repos verbosely
            </FormHelperText>
          </FormGroup>
          <AceEditor mode="sh" theme="monokai" value={script} readonly/>
        </DialogContent>
        <DialogActions>
          <Button
            variant={'contained'}
            color={'primary'}
            onClick={() => downloadTextFile(
              `clone-${assignment?.name}-repos.sh`,
              script,
              'plain/txt',
            )}
          >
            Download Script
          </Button>
          <Button variant={'contained'} color={'primary'} onClick={handleClose}>OK</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
