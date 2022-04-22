import React from 'react';
import {useHistory} from 'react-router-dom';

import AssignmentOutlinedIcon from '@material-ui/icons/AssignmentOutlined';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Switch from '@material-ui/core/Switch';
import Item from '../../shared/Item/Item';
import {useStyles} from './UserItems.styles';

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
        // link={`/admin/user?userId=${id}`}
      >
      <Button onClick={logIn}>
        Log-in as
      </Button>
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

