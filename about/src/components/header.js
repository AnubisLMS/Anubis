import React, {useState} from 'react';
import {Logo, HeaderLink, PrimaryButton, Button} from './atoms';
import {useScreenSize} from "../hooks/useScreenSize";
import {FiMenu, FiX} from 'react-icons/fi';
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

const HeaderModal = ({callback}) => {
  return (
    <div className= 'w-full bg-gray-800 rounded-md p-4 relative'>
      <div  onClick = {() => callback()}className= 'absolute top-2 right-2 cursor-pointer hover:opacity-60'>
        <FiX  className= 'w-6 h-auto'/>
      </div>
      <div className= 'space-y-4'>
        <div className= 'grid grid-cols-3 grid-rows-2 gap-4'>
          {links.map((link, index) => (
            <div className= 'cols-span-1 row-span-1'>
              <HeaderLink key = {`${link.name}-${index}`} to={link.path}>{link.name}</HeaderLink>
            </div>
          ))}
        </div>
        <div  className = 'border-t-2 border-gray-700'/>
        <div className= 'flex flex-row items-center'>
          <PrimaryButton>Log In</PrimaryButton>
          <Button className= 'hover:text-primary'>Get Started</Button>
        </div>
      </div>
    </div>
  )
}

export const Header = () => {
  const screenSize = useScreenSize();
  const [isModal, setIsModal] = useState(false);

  if (isModal) return (
    <HeaderModal  callback = {() => {setIsModal(false)}}/>
  )

  return (
    <div className= 'flex flex-row w-full h-20 justify-between items-center'>

      <div>
        <Logo />
      </div>

      {screenSize === 'lg' &&
        <div className= 'space-x-10'>
          {links.map((link, index) => (
            <HeaderLink key = {`${link.name}-${index}`} to={link.path}>{link.name}</HeaderLink>
          ))}
        </div>
      }

      {screenSize === 'lg' &&
        <div className= 'space-x-2'>
          <PrimaryButton>Log In</PrimaryButton>
          <Button className= 'hover:text-primary'>Get Started</Button>
        </div>
      }

      {screenSize !== 'lg' &&
        <div onClick={() => setIsModal(true)} className= 'bg-gray-800 rounded-full pr-4 pl-4 pt-2 pb-2 hover:bg-gray-700 cursor-pointer'>
          <FiMenu  className= 'w-6 h-auto'/>
        </div>
      }

    </div>
  )
}

export default Header;
