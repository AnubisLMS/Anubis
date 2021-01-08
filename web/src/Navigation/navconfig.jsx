import React from 'react';
import SchoolIcon from '@material-ui/icons/School';
import AssignmentOutlinedIcon from '@material-ui/icons/AssignmentOutlined';
import AssessmentIcon from '@material-ui/icons/Assessment';
import CodeOutlinedIcon from '@material-ui/icons/CodeOutlined';
import GitHubIcon from '@material-ui/icons/GitHub';
import AccountCircleOutlinedIcon from '@material-ui/icons/AccountCircleOutlined';
import PublicIcon from '@material-ui/icons/Public';


export const footerconfig = [{
  id: 'About',
  icon: <PublicIcon/>,
  path: '/about',
  Page: 'div',
}];

export const navconfig = [
  {
    id: 'Anubis',
    children: [
      {
        id: 'Courses',
        icon: <SchoolIcon/>,
        path: '/courses',
        Page: 'div',
      },
      {
        id: 'Assignments',
        icon: <AssignmentOutlinedIcon/>,
        path: '/courses/assignments',
        Page: 'div',
      },
      {
        id: 'Repos',
        icon: <GitHubIcon/>,
        path: '/repos',
        Page: 'div',
      },
      {
        id: 'Submissions',
        icon: <AssessmentIcon/>,
        path: '/courses/assignments/submissions',
        Page: 'div',
      },
      {
        id: 'Anubis IDE',
        icon: <CodeOutlinedIcon/>,
        path: '/ide',
        Page: 'div',
      },
      {
        id: 'Profile',
        icon: <AccountCircleOutlinedIcon/>,
        path: '/profile',
        Page: 'div',
      },
    ],
  },
];

export const drawerWidth = 240;
