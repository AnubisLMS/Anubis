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
import ImportContactsIcon from '@material-ui/icons/ImportContacts';
import DashboardIcon from '@material-ui/icons/Dashboard';

import Dashboard from './Pages/Public/Dashboard/Dashboard';
import Courses from './Pages/Public/Courses/Courses';
import Assignments from './Pages/Public/Assignments';
import Profile from './Pages/Public/Profile/Profile';
import Repos from './Pages/Public/Repos/Repos';
import Submissions from './Pages/Public/Submissions/Submissions';
import Submission from './Pages/Public/Submission/Submission';
import Blog from './Pages/Public/Blog';
import Visuals from './Pages/Public/Visuals/Visuals';
import Lectures from './Pages/Public/Lectures/Lectures';
import Playgrounds from './Pages/Public/Playgrounds/Playgrounds';

import Assignment from './Pages/Public/Assignment/Assignment';
import Course from './Pages/Public/Course/Course';
import AdminUsers from './Pages/Admin/Users';
import AdminUser from './Pages/Admin/User';
import AdminCourse from './Pages/Admin/Course';
import AdminTheia from './Pages/Admin/Theia';
import AdminStatic from './Pages/Admin/Static';
import AdminLectures from './Pages/Admin/Lectures';
import AdminAutogradeAssignments from './Pages/Admin/Autograde/Assignments';
import AdminAutogradeSubmission from './Pages/Admin/Autograde/Submission';
import AdminAutogradeResults from './Pages/Admin/Autograde/Results';
import AdminAssignmentLateExceptions from './Pages/Admin/Assignment/LateExceptions';
import AdminAssignmentAssignments from './Pages/Admin/Assignment/Assignments';
import AdminAssignmentAssignment from './Pages/Admin/Assignment/Assignment';
import AdminAssignmentQuestions from './Pages/Admin/Assignment/Questions';
import AdminAssignmentTests from './Pages/Admin/Assignment/Tests';
import AdminAssignmentRepos from './Pages/Admin/Assignment/Repos';
import AdminAssignmentGroups from './Pages/Admin/Assignment/AssignmentGroups';

// Super
import SuperConfig from './Pages/Super/Config';
import SuperIDEImages from './Pages/Super/IDEImages';
import SuperPlaygrounds from './Pages/Super/Playgrounds';


export const footer_nav = [
  {
    id: 'Visuals',
    icon: <TimelineIcon/>,
    exact: true,
    path: '/visuals',
    Page: Visuals,
  },
  {
    id: 'Playgrounds',
    icon: <i className="devicon-vscode-plain" style={{fontSize: 20}}/>,
    path: '/playgrounds',
    Page: Playgrounds,
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
        id: 'Dashboard',
        icon: <DashboardIcon/>,
        path: '/dashboard',
        Page: Dashboard,
      },
      {
        id: 'Courses',
        icon: <SchoolIcon/>,
        path: '/courses',
        Page: Courses,
      },
      {
        id: 'Lectures',
        icon: <ImportContactsIcon/>,
        path: '/lectures',
        Page: Lectures,
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
    id: 'Course',
    icon: <SchoolIcon/>,
    path: '/admin/course',
    Page: AdminCourse,
    exact: false,
  },
  {
    id: 'Lectures',
    icon: <ImportContactsIcon/>,
    path: '/admin/lectures',
    Page: AdminLectures,
  },
  {
    id: 'Assignments',
    icon: <AssignmentOutlinedIcon/>,
    path: '/admin/assignments',
    Page: AdminAssignmentAssignments,
  },
  {
    id: 'Autograde Results',
    icon: <PieChartIcon/>,
    path: '/admin/autograde',
    Page: AdminAutogradeAssignments,
  },
  {
    id: 'Anubis Cloud IDE',
    icon: <i className="devicon-vscode-plain" style={{fontSize: 20}}/>,
    path: '/admin/ide',
    Page: AdminTheia,
  },
  {
    id: 'Static',
    icon: <AttachFileIcon/>,
    path: '/admin/static',
    Page: AdminStatic,
  },
];

export const super_nav = [
  {
    id: 'Playgrounds',
    icon: <i className="devicon-vscode-plain" style={{fontSize: 20}}/>,
    path: '/super/playgrounds',
    Page: SuperPlaygrounds,
  },
  {
    id: 'IDE Images',
    icon: <i className="devicon-docker-plain" style={{fontSize: 20}}/>,
    path: '/super/ide-images',
    Page: SuperIDEImages,
  },
  {
    id: 'Config',
    icon: <SettingsIcon/>,
    path: '/super/config',
    Page: SuperConfig,
  },
];

export const not_shown_nav = [
  {
    id: 'Submission',
    path: '/submission',
    Page: Submission,
  },
  {
    id: 'Assignment',
    path: '/courses/assignment',
    Page: Assignment,
  },
  {
    id: 'Course',
    path: '/course',
    Page: Course,
  },
  {
    id: 'User',
    path: '/admin/user',
    Page: AdminUser,
  },
  {
    id: 'AdminAssignmentResults',
    path: '/admin/autograde/assignment/:assignmentId',
    Page: AdminAutogradeResults,
  },
  {
    id: 'AdminSubmissionStats',
    path: '/admin/autograde/submission',
    Page: AdminAutogradeSubmission,
  },
  {
    id: '',
    path: '/admin/assignment/questions/:assignmentId',
    Page: AdminAssignmentQuestions,
  },
  {
    id: '',
    path: '/admin/assignment/tests/:assignmentId',
    Page: AdminAssignmentTests,
  },
  {
    id: '',
    path: '/admin/assignment/repos/:assignmentId',
    Page: AdminAssignmentRepos,
  },
  {
    id: '',
    path: '/admin/assignment/edit/:assignmentId',
    Page: AdminAssignmentAssignment,
  },
  {
    id: '',
    path: '/admin/assignment/late-exceptions/:assignmentId',
    Page: AdminAssignmentLateExceptions,
  },
  {
    id: '',
    path: '/admin/assignment/groups/:assignmentId',
    Page: AdminAssignmentGroups,
  },

];

export const drawerWidth = 240;
