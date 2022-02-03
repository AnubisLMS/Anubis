import React from 'react';
import {useHistory} from 'react-router-dom';

import AssignmentOutlinedIcon from '@material-ui/icons/AssignmentOutlined';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Item from '../../shared/Item/Item';
import {useStyles} from './UserItems.styles';

const UserItem = ({
  id,
  netid,
  name,
  githubUsername,
  privileged = false,
}) => {
  const history = useHistory();

  return (
    <Item
      showStatus={false}
      title={name}
      subTitle={`from: ${netid}`}
      titleIcon={<AssignmentOutlinedIcon/>}
      link={`/admin/user?userId=${id}`}
    >
      <Typography>
        {githubUsername}
      </Typography>
      {!privileged && (<Typography>{netid}</Typography>)}
      <Button onClick={() => history.push(`/admin/user?userId=${id}`)}>
        View User
      </Button>
    </Item>
  );
};

export default UserItem;

