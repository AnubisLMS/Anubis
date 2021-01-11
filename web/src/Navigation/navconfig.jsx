import React from 'react';

import SchoolIcon from '@material-ui/icons/School';
import AssignmentOutlinedIcon from '@material-ui/icons/AssignmentOutlined';
import AssessmentIcon from '@material-ui/icons/Assessment';
import CodeOutlinedIcon from '@material-ui/icons/CodeOutlined';
import GitHubIcon from '@material-ui/icons/GitHub';
import AccountCircleOutlinedIcon from '@material-ui/icons/AccountCircleOutlined';
import PublicIcon from '@material-ui/icons/Public';

import About from '../Pages/About';
import Courses from '../Pages/Courses';
import Assignments from '../Pages/Assignments';
import IDE from '../Pages/IDE';
import Profile from '../Pages/Profile';
import Repos from '../Pages/Repos';
import Submissions from '../Pages/Submissions';

export const footerconfig = [{
  id: 'About',
  icon: <PublicIcon/>,
  path: '/about',
  Page: About,
}];

export const navconfig = [
  {
    id: 'Anubis',
    children: [
      {
        id: 'Courses',
        icon: <SchoolIcon/>,
        path: '/courses',
        Page: Courses,
      },
      {
        id: 'Assignments',
        icon: <AssignmentOutlinedIcon/>,
        path: '/courses/assignments',
        Page: Assignments,
      },
      {
        id: 'Repos',
        icon: <GitHubIcon/>,
        path: '/repos',
        Page: Repos,
      },
      {
        id: 'Submissions',
        icon: <AssessmentIcon/>,
        path: '/courses/assignments/submissions',
        Page: Submissions,
      },
      {
        id: 'Anubis IDE',
        icon: <CodeOutlinedIcon/>,
        path: '/ide',
        Page: IDE,
      },
      {
        id: 'Profile',
        icon: <AccountCircleOutlinedIcon/>,
        path: '/profile',
        Page: Profile,
      },
    ],
  },
];

export const drawerWidth = 240;
