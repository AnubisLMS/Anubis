import React from 'react';
import {Layout, FeatureCard} from '../components';
import {PageTitle} from '../components/atoms';

const features = [
  {
    name: 'Grading Insights',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec vestibulum velit.'
  },
  {
    name: 'Auto Grader',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec vestibulum velit.',
  },
  {
    name: 'Submission',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec vestibulum velit.',
  },
  {
    name: 'Customizibility',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec vestibulum velit.',
  },
  {
    name: 'Virtual IDE',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec vestibulum velit.',
  },
  {
    name: 'Class Management',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec vestibulum velit.'
  }
]

export const Features = () => {
  return (
    <Layout>
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
