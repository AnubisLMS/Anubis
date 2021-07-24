import React, {useState} from 'react';
import {StaticImage} from "gatsby-plugin-image";
import ideGIF from '../../images/ide.gif';
const tabs = [
  {
    title: 'Assignments',
    id: 'assignments',
  },
  {
    title: 'Submissions',
    id: 'submissions',
  },
  {
    title: 'IDEs',
    id: 'ides',
  },
  {
    title: 'Grading',
    id: 'grading',
  }
];

const TabSelector = ({active = false, children, onClick = () => {}}) => (
  <p className={active ? 'text-light-100 pb-2 border-b-2 border-light-100': 'text-light-400 hover:text-light-200 cursor-pointer pb-2'} onClick = {onClick}>{children}</p>
)

const Showcase = () => {
  const [selectedTab, setSelectedTab] = useState('ides');
  return (
    <div className = 'w-full flex-col flex items-center'>
      {/*<div className= 'w-full h-screen/3 bg-light-500 rounded-lg bg-ide bg-cover'></div>*/}
      <img className= 'w-full h-full h-screen43 rounded-lg' src = {ideGIF} />
      <div className= 'flex flex-row items-center justify-between p-4 space-x-6 text-light-300'>
        {tabs.map((tab, index) => (
          <TabSelector onClick = {() => setSelectedTab(tab.id)} active = {selectedTab === tab.id} key = {`${index}-${tab.id}`}>{tab.title}</TabSelector>
        ))}
      </div>
    </div>
  )
}

export default Showcase;