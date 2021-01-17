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

import AdminUsers from '../Pages/Admin/Users';
import AdminUser from '../Pages/Admin/User';
import AdminAssignments from '../Pages/Admin/Assignments';

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
    id: 'Students',
    icon: <GroupIcon/>,
    path: '/admin/users',
    Page: AdminUsers,
  },
  {
    id: 'Assignments',
    icon: <PieChartIcon/>,
    path: '/admin/assignments',
    Page: AdminAssignments,
  },
  {
    id: 'Courses',
    icon: <SettingsIcon/>,
    path: '/admin/courses',
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
    path: '/admin/user',
    Page: AdminUser,
  },
];

export const drawerWidth = 240;
