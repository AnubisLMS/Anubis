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
    name: 'Demo',
    path: '/demo'
  },
  {
    name: 'Contribute',
    path: '/Contribute',
  },
];

export const Header = () => {
  return (
    <div className= 'flex flex-row w-full h-20 justify-between items-center' style = {{border: '1px solid red'}}>
      <div>
        <Logo />
      </div>

      <div className= 'space-x-10'>
        {links.map((link, index) => (
          <HeaderLink key = {`${link.name}-${index}`} to={link.path}>{link.name}</HeaderLink>
        ))}
      </div>

      <div className= 'space-x-5'>
        <PrimaryButton>Log In</PrimaryButton>
        <Button>Get Started</Button>


      </div>
    </div>
  )
}

export default Header;
