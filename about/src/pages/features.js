import React from 'react';
import {Layout, FeatureCard} from '../components';
import {PageTitle} from '../components/atoms';
import {GradingIcon, GraderIcon, SubmissionIcon, CustomIcon, VirtualIcon, ManagementIcon} from "../components/atoms";

import {useScreenSize} from '../hooks/useScreenSize';

const features = [
  {
    name: 'Grading Insights',
    shortDescription: 'Get quantitative data on how topics and assignments are comprehended',
    icon: (secondary) => (<GradingIcon isSecondary={secondary}/> )
  },
  {
    name: 'Auto Grader',
    shortDescription: 'Accelerate grading by automating the grunt work out',
    icon: (secondary) => (<GraderIcon isSecondary={secondary}/> )
  },
  {
    name: 'Submission',
    shortDescription: 'Submit assignments as many times as needed getting live feedback as students go',
    icon: (secondary) => (<SubmissionIcon isSecondary={secondary}/> )
  },
  {
    name: 'Customizability',
    shortDescription: 'Integrate only the parts of Anubis that fit in the curriculum',
    icon: (secondary) => (<CustomIcon isSecondary={secondary}/> )
  },
  {
    name: 'Cloud IDE',
    shortDescription: 'Prebuilt linux IDEs in the cloud tailored to each course\'s needs',
    icon: (secondary) => (<VirtualIcon isSecondary={secondary}/> )
  },
  {
    name: 'Class Management',
    shortDescription: 'Administrate with Anubis\'s complete admin panel and Management IDEs',
    icon: (secondary) => (<ManagementIcon isSecondary={secondary}/> )
  }
]


export const Features = () => {
  const screenSize = useScreenSize();
  return (
    <Layout isCentered >
      <div className = 'flex flex-row items-start max-w-6xl p-4'>
        <PageTitle className = 'border-b-2 border-primary pb-2'>Features</PageTitle>
      </div>

      <div className= {`mt-6 grid max-w-6xl ${screenSize === 'lg' ? 'grid-cols-3' : screenSize === 'md' ? 'grid-cols-2'  : 'grid-cols-1'} gap-4`}>
        {features.map((feature, index) => (
          <FeatureCard {... feature} key = {`${feature.name}-${index}`}/>
        ))}
      </div>
    </Layout>
  )
};

export default Features;
