import React from 'react';
import {Redirect} from 'react-router-dom';

import SchoolIcon from '@material-ui/icons/School';
import AssignmentOutlinedIcon from '@material-ui/icons/AssignmentOutlined';
import AssessmentIcon from '@material-ui/icons/Assessment';
import GitHubIcon from '@material-ui/icons/GitHub';
import AccountCircleOutlinedIcon from '@material-ui/icons/AccountCircleOutlined';
import GroupIcon from '@material-ui/icons/Group';
import SettingsIcon from '@material-ui/icons/Settings';
import PieChartIcon from '@material-ui/icons/PieChart';
import AttachFileIcon from '@material-ui/icons/AttachFile';
import BookIcon from '@material-ui/icons/Book';
import TimelineIcon from '@material-ui/icons/Timeline';
import ImportContactsIcon from '@material-ui/icons/ImportContacts';
import DashboardIcon from '@material-ui/icons/Dashboard';

import Dashboard from './pages/core/public/Dashboard/Dashboard';
import Courses from './pages/core/public/Courses/Courses';
import Assignments from './pages/core/public/Assignments';
import Profile from './pages/core/public/Profile/Profile';
import Repos from './pages/core/public/Repos/Repos';
import Submissions from './pages/core/public/Submissions/Submissions';
import Submission from './pages/core/public/Submission/Submission';
import Blog from './pages/core/public/Blog';
import Visuals from './pages/core/public/Visuals/Visuals';
import Lectures from './pages/core/public/Lectures/Lectures';
import Playgrounds from './pages/core/public/Playgrounds/Playgrounds';
import PrivacyPolicy from './pages/core/public/PrivacyPolicy/PrivacyPolicy';

import Assignment from './pages/core/public/Assignment/Assignment';
import Course from './pages/core/public/Course/Course';
import AdminUsers from './pages/core/admin/Users';
import AdminUser from './pages/core/admin/User';
import AdminCourse from './pages/core/admin/Course';
import AdminTheia from './pages/core/admin/Theia';
import AdminStatic from './pages/core/admin/Static';
import AdminLectures from './pages/core/admin/Lectures';
import AdminAutogradeAssignments from './pages/core/admin/Autograde/Assignments';
import AdminAutogradeSubmission from './pages/core/admin/Autograde/Submission';
import AdminAutogradeResults from './pages/core/admin/Autograde/Results';
import AdminAssignmentLateExceptions from './pages/core/admin/Assignment/LateExceptions';
import AdminAssignmentAssignments from './pages/core/admin/Assignment/Assignments';
import AdminAssignmentAssignment from './pages/core/admin/Assignment/Assignment';
import AdminAssignmentQuestions from './pages/core/admin/Assignment/Questions';
import AdminAssignmentTests from './pages/core/admin/Assignment/Tests';
import AdminAssignmentRepos from './pages/core/admin/Assignment/Repos';
import AdminAssignmentGroups from './pages/core/admin/Assignment/AssignmentGroups';

// super
import SuperConfig from './pages/core/super/Config';
import SuperIDEImages from './pages/core/super/IDEImages';
import SuperPlaygrounds from './pages/core/super/Playgrounds';
import SuperUsers from './pages/core/super/Users';


export const footer_nav = [
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
  {
    id: 'Playgrounds',
    icon: <i className="devicon-vscode-plain" style={{fontSize: 20}}/>,
    path: '/playgrounds',
    Page: Playgrounds,
  },

  {
    id: 'Privacy Policy',
    icon: <i className="devicon-vscode-plain" style={{fontSize: 20}}/>,
    path: '/privacypolicy',
    Page: PrivacyPolicy,
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
    id: 'IDE images',
    icon: <i className="devicon-docker-plain" style={{fontSize: 24}}/>,
    path: '/super/ide-images',
    Page: SuperIDEImages,
  },
  {
    id: 'Config',
    icon: <SettingsIcon/>,
    path: '/super/config',
    Page: SuperConfig,
  },
  {
    id: 'Users',
    icon: <GroupIcon/>,
    path: '/super/users',
    Page: SuperUsers,
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
  {
    id: '',
    path: '/v',
    Page: () => <Redirect to={'/visuals'}/>,
  },
];

export const drawerWidth = 240;
