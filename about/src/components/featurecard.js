import React, {useState} from 'react';

import {GradingIcon} from './atoms';

const FeatureCard = ({name, shortDescription, icon}) => {
  const [secondary, setSecondary] = useState(false);
  return (
    <div onMouseOver = {() => setSecondary(true)}  onMouseLeave = {() => setSecondary(false)} className = 'flex  flex-row justify-center items-center border-2 h-32 border-primary p-6 hover:bg-primary hover:text-black cursor-pointer space-x-2'>
      <div>
        {icon(secondary)}
      </div>
      <div>
        <h1 className= 'text-md font-bold'>{name}</h1>
        <p className= 'text-sm'>{shortDescription}</p>
      </div>
    </div>
  )
}

export default FeatureCard;