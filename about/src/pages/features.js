import React from 'react';
import {Layout} from '../components';

//motion lib import
import {motion} from 'framer-motion';

//svg imports
import customIcon from '../images/svg/custom.svg';
import gradeIcon from '../images/svg/grade.svg';
import ideIcon from '../images/svg/ide.svg';
import insightsIcon from '../images/svg/insights.svg';
import manageIcon from '../images/svg/manage.svg';
import submissionIcon from '../images/svg/submission.svg';
import {FiArrowRight} from "react-icons/fi";

//import yummy hook
import {useScreenSize} from '../hooks/useScreenSize';


const features = [
  {
    name: 'Grading Insights',
    shortDescription: 'Get quantitative data on how topics and assignments are comprehended',
    icon: insightsIcon
  },
  {
    name: 'Auto Grader',
    shortDescription: 'Accelerate grading by automating the grunt work out',
    icon: gradeIcon
  },
  {
    name: 'Submission',
    shortDescription: 'Submit assignments as many times as needed getting live feedback as students go',
    icon: submissionIcon
  },
  {
    name: 'Customizibility',
    shortDescription: 'Integrate only the parts of Anubis that fit in the curriculum',
    icon: customIcon
  },
  {
    name: 'Cloud IDE',
    shortDescription: 'Prebuilt linux IDEs in the cloud tailored to each course\'s needs',
    icon: ideIcon
  },
  {
    name: 'Class Management',
    shortDescription: 'Administrate with Anubis\'s complete admin panel and Management IDEs',
    icon: manageIcon
  }
]

const Features = () => {

  const screenSize = useScreenSize();

  const arrowButtonVariant = {
    hover: {
      opacity: 1,
    },
    initial: {
      opacity: 0,
    },
  };

  const parentVariant = {
    hover: {
      scale: 1.04
    },
  }

  return (
    <Layout>
      <div className= 'flex flex-col max-w-5xl w-full items-start justify-center  space-y-24 inline pt-20'>
        <h1 className= 'text-6xl  font-gosha w-full'><span className= 'text-primary'>~</span> Features</h1>
        <div className= 'w-full grid grid-cols-4 gap-8 pl-6 pr-6'>
          {features.map((feature, index) => (
            <motion.li
              variants = {parentVariant}
              className= {`${(screenSize === 'lg' || screenSize === 'md') ? 'col-span-2 justify-center': 'col-span-4 justify-start'} flex flex-row items-center  space-x-2 bg-light-600 p-4 space-x-4 rounded-lg cursor-pointer`}
              layout initial="initial" whileHover="hover"
            >
              <img className= 'w-14 h-auto' src = {feature.icon} />
              <div className= 'flex flex-col'>
                <h1 className= 'text-lg  font-bold text-light-100'>{feature.name}</h1>
                <p className= 'text-light-400'>{feature.shortDescription}</p>
              </div>
              <motion.div variants = {arrowButtonVariant} transition={{duration: 0.25}}>
                <FiArrowRight className='w-6 h-auto' />
              </motion.div>
            </motion.li>
          ))}
        </div>

      </div>
    </Layout>
  )
};

export default Features;
