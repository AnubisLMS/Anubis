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
import AttachFileIcon from '@material-ui/icons/AttachFile';
import BookIcon from '@material-ui/icons/Book';
import TimelineIcon from '@material-ui/icons/Timeline';

import About from '../Pages/Public/About';
import Courses from '../Pages/Public/Courses';
import Assignments from '../Pages/Public/Assignments';
import Profile from '../Pages/Public/Profile';
import Repos from '../Pages/Public/Repos';
import Submissions from '../Pages/Public/Submissions';
import Submission from '../Pages/Public/Submission';
import Blog from '../Pages/Public/Blog';
import Visuals from '../Pages/Public/Visuals';

import AdminUsers from '../Pages/Admin/Users';
import AdminUser from '../Pages/Admin/User';
import AdminAssignments from '../Pages/Admin/Assignment/Assignments';
import AdminStats from '../Pages/Admin/Autograde/AutogradeResults';
import AdminAssignmentStats from '../Pages/Admin/Autograde/AutogradeAssignments';
import AdminSubmissionStats from '../Pages/Admin/Autograde/AutogradeSubmission';
import AdminCourses from '../Pages/Admin/Courses';
import AdminTheia from '../Pages/Admin/Theia';
import AdminStatic from '../Pages/Admin/Static';
import AdminConfig from '../Pages/Admin/Config';
import AdminAssignmentQuestions from '../Pages/Admin/Assignment/AssignmentQuestions';
import AdminAssignmentTests from '../Pages/Admin/Assignment/AssignmentTests';

export const footer_nav = [
  {
    id: 'About',
    icon: <PublicIcon/>,
    exact: true,
    path: '/about',
    Page: About,
  },
  {
    id: 'Visuals',
    icon: <TimelineIcon/>,
    exact: true,
    path: '/visuals',
    Page: Visuals,
  },
  {
    id: 'Blog',
    icon: <BookIcon/>,
    exact: false,
    path: '/blog',
    Page: Blog,
  },
];

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
    id: 'Courses',
    icon: <SchoolIcon/>,
    path: '/admin/courses',
    Page: AdminCourses,
  },
  {
    id: 'Assignments',
    icon: <AssignmentOutlinedIcon/>,
    path: '/admin/assignments',
    Page: AdminAssignments,
  },
  {
    id: 'Autograde Results',
    icon: <PieChartIcon/>,
    path: '/admin/autograde',
    Page: AdminStats,
  },
  {
    id: 'Anubis Cloud IDE',
    icon: <CodeOutlinedIcon/>,
    path: '/admin/ide',
    Page: AdminTheia,
  },
  {
    id: 'Static',
    icon: <AttachFileIcon/>,
    path: '/admin/static',
    Page: AdminStatic,
  },
  {
    id: 'Config',
    icon: <SettingsIcon/>,
    path: '/admin/config',
    Page: AdminConfig,
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
  {
    id: 'AdminAssignmentStats',
    path: '/admin/autograde/assignment',
    Page: AdminAssignmentStats,
  },
  {
    id: 'AdminSubmissionStats',
    path: '/admin/autograde/submission',
    Page: AdminSubmissionStats,
  },
  {
    id: '',
    path: '/admin/assignment/questions/:code',
    Page: AdminAssignmentQuestions,
  },
  {
    id: '',
    path: '/admin/assignment/tests/:assignmentId',
    Page: AdminAssignmentTests,
  },
];

export const drawerWidth = 240;
