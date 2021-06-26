export default [
  {
    slug: 'elavator-pitch',
    title: 'Anubis LMS',
    author: 'John Cunniff',
    authorImage: 'https://avatars.githubusercontent.com/u/36013983',
    date: '2021-03-17',
    isHighlight: true,
    get: () => {
      return import('./ElavatorPitch.md');
    },
  },
  {
    slug: 'anubis-cloud-ide',
    title: 'Anubis cloud IDEs',
    author: 'John Cunniff',
    authorImage: 'https://avatars.githubusercontent.com/u/36013983',
    date: '2021-04-13',
    get: () => {
      return import('./TheialDE.md');
    },
  },
  {
    slug: 'midterm-retro',
    title: 'Reorganizing RPC While Under Load - The Midterm Retro',
    author: 'John Cunniff',
    authorImage: 'https://avatars.githubusercontent.com/u/36013983',
    date: '2021-04-06',
    get: () => {
      return import('./MidtermRetro.md');
    },
  },
  {
    slug: 'assignment-packaging',
    title: 'Assignment Packaging',
    author: 'John Cunniff',
    authorImage: 'https://avatars.githubusercontent.com/u/36013983',
    date: '2021-03-31',
    get: () => {
      return import('./AssignmentPackaging.md');
    },
  },
  {
    slug: 'packaging',
    title: 'How Assignments Work In Anubis',
    author: 'John Cunniff',
    authorImage: 'https://avatars.githubusercontent.com/u/36013983',
    date: '2021-03-24',
    get: () => {
      return import('./Assignment.md');
    },
  },

];
