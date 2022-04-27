import React from 'react';
import {useHistory} from 'react-router-dom';

import AssignmentOutlinedIcon from '@material-ui/icons/AssignmentOutlined';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Switch from '@material-ui/core/Switch';
import ExitToAppIcon from '@material-ui/icons/ExitToApp';
import Item from '../../shared/Item/Item';

const SuperUserItem = ({
  id,
  netid,
  name,
  githubUsername,
  logIn,
  superuser,
  student,
  privileged = false,
}) => {
  const history = useHistory();

  return (
    <Item
      showStatus={false}
      title={name}
      subTitle={`from: ${netid}`}
      titleIcon={<AssignmentOutlinedIcon/>}
    >
      <ExitToAppIcon onClick={logIn} />
      <Typography>
        {githubUsername}
      </Typography>
      {!privileged && (<Typography>{netid}</Typography>)}
      <Button onClick={() => history.push(`/admin/user?userId=${id}`)}>
        View User
      </Button>
      <Switch
        checked={student.is_superuser}
        color={'primary'}
        onClick={superuser}
      />
    </Item>
  );
};

export default SuperUserItem;

