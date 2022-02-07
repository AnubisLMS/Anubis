export default [
  {
    slug: 'git-vuln',
    title: 'Abusing Anubis Autosave to Break into Student GitHub Repositories',
    author: 'Alan Cao',
    authorImage: 'https://avatars.githubusercontent.com/u/17283637?',
    date: '2022-02-06',
    get: () => {
      return import("./GitVuln.md");
    },
  },
  {
    slug: 'proxy-vuln',
    title: 'Proxy Cache Vulnerability',
    author: 'John Cunniff',
    authorImage: 'https://avatars.githubusercontent.com/u/36013983',
    date: '2022-01-25',
    get: () => {
      return import('./ProxyVuln.md');
    },
  },
  {
    slug: 'elavator-pitch',
    title: 'Anubis LMS',
    author: 'John Cunniff',
    authorImage: 'https://avatars.githubusercontent.com/u/36013983',
    date: '2021-03-17',
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
