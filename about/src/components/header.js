import React from 'react';
import {Logo, HeaderLink, PrimaryButton, Button} from './atoms';

const links = [
  {
    name: 'Home',
    path: '/'
  },
  {
    name: 'Features',
    path: '/features'
  },
  {
    name: 'Blog',
    path: '/blog'
  },
  {
    name: 'Contribute',
    path: '/contribute',
  },
  {
    name: 'Contact Us',
    path: '/contact'
  }
];

export const Header = () => {
  return (
    <div className= 'flex flex-row w-full h-20 justify-between items-center'>
      <div>
        <Logo />
      </div>
      <div className= 'space-x-10'>
        {links.map((link, index) => (
          <HeaderLink key = {`${link.name}-${index}`} to={link.path}>{link.name}</HeaderLink>
        ))}
      </div>
      <div className= 'space-x-2'>
        <PrimaryButton>Log In</PrimaryButton>
        <Button className= 'hover:text-primary'>Get Started</Button>
      </div>
    </div>
  )
}

export default Header;
