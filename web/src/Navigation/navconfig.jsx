import React from 'react';

import SchoolIcon from '@material-ui/icons/School';
import AssignmentOutlinedIcon from '@material-ui/icons/AssignmentOutlined';
import AssessmentIcon from '@material-ui/icons/Assessment';
import CodeOutlinedIcon from '@material-ui/icons/CodeOutlined';
import GitHubIcon from '@material-ui/icons/GitHub';
import AccountCircleOutlinedIcon from '@material-ui/icons/AccountCircleOutlined';
import PublicIcon from '@material-ui/icons/Public';
import GroupIcon from '@material-ui/icons/Group';
import SettingsIcon from '@material-ui/icons/Settings';
import PieChartIcon from '@material-ui/icons/PieChart';

import About from '../Pages/Public/About';
import Courses from '../Pages/Public/Courses';
import Assignments from '../Pages/Public/Assignments';
import IDE from '../Pages/Public/IDE';
import Profile from '../Pages/Public/Profile';
import Repos from '../Pages/Public/Repos';
import Submissions from '../Pages/Public/Submissions';
import Submission from '../Pages/Public/Submission';

import Users from '../Pages/Admin/Users';
import User from '../Pages/Admin/User';

export const footer_nav = [{
  id: 'About',
  icon: <PublicIcon/>,
  exact: true,
  path: '/about',
  Page: About,
}];

export const public_nav = [
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
        id: 'Repos',
        icon: <GitHubIcon/>,
        path: '/repos',
        Page: Repos,
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


export const admin_nav = [
  {
    id: 'StudentStats',
    icon: <GroupIcon/>,
    path: '/users',
    Page: Users,
  },
  {
    id: 'AssignmentStats',
    icon: <PieChartIcon/>,
    path: '/assingmentstats',
    Page: Courses,
  },
  {
    id: 'Courses',
    icon: <SettingsIcon/>,
    path: '/assingmentstats',
    Page: Courses,
  },
];

export const not_shown_nav = [
  {
    id: 'Submission',
    path: '/submission',
    Page: Submission,
  },
  {
    id: 'User',
    path: '/user',
    Page: User,
  },
];

export const drawerWidth = 240;
