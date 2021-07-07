import React from 'react';
import {Layout, FeatureCard} from '../components';
import {PageTitle} from '../components/atoms';
import {GradingIcon, GraderIcon, SubmissionIcon, CustomIcon, VirtualIcon, ManagementIcon} from "../components/atoms";

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
  return (
    <Layout isCentered>
      <div className= 'flex items-start w-full max-w-6xl'>
        <PageTitle>Features</PageTitle>
      </div>
      <div className= 'grid max-w-6xl grid-cols-3 gap-4'>
        {features.map((feature, index) => (
          <FeatureCard {... feature} />
        ))}
      </div>
    </Layout>
  )
};

export default Features;
