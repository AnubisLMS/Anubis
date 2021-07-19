import React, {useState} from 'react';
import {Logo, HeaderLink, SecondaryButton, PrimaryButton, Button} from './atoms';
import {useScreenSize} from "../hooks/useScreenSize";
import {FiMenu, FiX} from 'react-icons/fi';
const links = [
  {
    name: 'Documentation',
    path: '/documentation'
  },
  {
    name: 'Blog',
    path: '/blog'
  },
  {
    name: 'Contact',
    path: '/contact',
  }
];

const HeaderModal = ({callback}) => {
  return (
    <div className= 'w-full mt-4 rounded-md relative'>
      <div className= 'space-y-4'>
        <div className= 'flex flex-col w-full items-start justify-center  space-y-4'>
          {links.map((link, index) => (
            <div className= 'border-b-2 border-light-500 w-full pb-4 '>
              <HeaderLink key = {`${link.name}-${index}`} to={link.path}>{link.name}</HeaderLink>
            </div>
          ))}
        </div>
        <div className= 'flex flex-row w-full items-start'>
          <SecondaryButton>Log In</SecondaryButton>
        </div>
      </div>
    </div>
  )
}

export const Header = () => {
  const screenSize = useScreenSize();
  const [isModal, setIsModal] = useState(false);

  return (
    <div className= 'flex flex-col w-full p-4'>
      <div className= 'flex flex-row w-full h-20  justify-between items-center'>
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
          <SecondaryButton>Log In</SecondaryButton>
        </div>
        }

        {screenSize !== 'lg' &&
        <div onClick={() => setIsModal(!isModal)} className= 'bg-gray-800 rounded-full pr-4 pl-4 pt-2 pb-2 hover:bg-gray-700 cursor-pointer'>
          <FiMenu  className= 'w-6 h-auto'/>
        </div>
        }
      </div>
      {isModal && screenSize !== 'lg'  &&
        <HeaderModal  callback = {() => {setIsModal(false)}}/>
      }

    </div>
  )
}

export default Header;
