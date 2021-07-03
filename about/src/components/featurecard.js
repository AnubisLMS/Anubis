import React from 'react';

const FeatureCard = ({name, description}) => {
  return (
    <div className= 'flex  flex-row justify-center items-center border-2 h-32 border-primary p-6 hover:bg-primary hover:text-black cursor-pointer'>
      <div>
        <h1 className= 'text-md font-bold'>{name}</h1>
        <p className= 'text-sm'>{description}</p>
      </div>
    </div>
  )
}

export default FeatureCard;