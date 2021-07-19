import React from 'react';
import assignmentsIcon from '../../images/svg/assignments.svg';
import analyticsIcon from '../../images/svg/analytics.svg';
import ideIcon from '../../images/svg/ide.svg';
import {useScreenSize} from "../../hooks/useScreenSize"

const features = [
  {
    name: 'Assignments',
    icon: assignmentsIcon,
    title: 'Curate Your Own Assignments',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec sed lectus et erat iaculis tempor id ut sem. Proin ultricies consectetur dolor, '
  },
  {
    name: 'IDEs',
    icon: ideIcon,
    title: 'Build Custom IDEs' ,
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec sed lectus et erat iaculis tempor id ut sem. Proin ultricies consectetur dolor, ',
  },
  {
    name: 'Grading',
    icon: analyticsIcon,
    title: 'View Grading Analytics',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec sed lectus et erat iaculis tempor id ut sem. Proin ultricies consectetur dolor, ',
  }
]

const HotFeatures = () => {
  const screen = useScreenSize();
  return (
    <div className= {`w-full grid grid-cols-3 gap-6`}>
      {features.map(({icon, title, description}, index) => (
        <div className= {`flex flex-col ${(screen !== 'lg') ? 'col-span-3 p-6': 'col-span-1'} items-start w-full space-y-4`}>
          <img alt = 'title' src = {icon} className= 'w-8 h-auto' />
          <div className= 'text-left'>
            <h2 className= 'text-lg text-light-100 '>{title}</h2>
            <p className= 'text-md text-light-400 text-left'>{description}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

export default HotFeatures;