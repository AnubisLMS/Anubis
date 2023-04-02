import React from 'react';
import {Redirect} from 'react-router-dom';

import SchoolIcon from '@mui/icons-material/School';
import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined';
import AssessmentIcon from '@mui/icons-material/Assessment';
import GitHubIcon from '@mui/icons-material/GitHub';
import AccountCircleOutlinedIcon from '@mui/icons-material/AccountCircleOutlined';
import GroupIcon from '@mui/icons-material/Group';
import SettingsIcon from '@mui/icons-material/Settings';
import PieChartIcon from '@mui/icons-material/PieChart';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import BookIcon from '@mui/icons-material/Book';
import TimelineIcon from '@mui/icons-material/Timeline';
import ImportContactsIcon from '@mui/icons-material/ImportContacts';
import DashboardIcon from '@mui/icons-material/Dashboard';
import EmailIcon from '@mui/icons-material/Email';
import EventIcon from '@mui/icons-material/Event';

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
import PrivacyPolicy from './pages/core/public/PrivacyPolicy';
import Assignment from './pages/core/public/Assignment/Assignment';
import Course from './pages/core/public/Course/Course';
import AprilFools from './pages/core/public/AprilFools';

import AdminReservations from './pages/core/admin/Reservations';
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
import EmailTemplates from './pages/core/super/EmailTemplates';
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
    id: 'Anubis NFT',
    icon: <img src={'/aprilfools/200w.gif'} style={{width: 22}} alt={'gif'}/>,
    path: '/aprilfools2023',
    Page: AprilFools,
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
  {
    id: 'Reservations',
    icon: <EventIcon/>,
    path: '/admin/reservations',
    Page: AdminReservations,
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
  {
    id: 'Email Templates',
    icon: <EmailIcon/>,
    path: '/super/email',
    Page: EmailTemplates,
  },
];

export const not_shown_nav = [
  {
    id: 'Submission',
    path: '/submission/:submissionId',
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
    path: '/privacy-policy',
    Page: PrivacyPolicy,
  },
  {
    id: '',
    path: '/v',
    Page: () => <Redirect to={'/visuals'}/>,
  },
];

export const drawerWidth = 240;
