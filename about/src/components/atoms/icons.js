import React from 'react';
import {StaticImage} from "gatsby-plugin-image";
import '../../images/svg/grading_primary.svg'

export const GradingIcon = ({isSecondary = false, primaryPath, secondaryPath}) => {
  return (
    <div>
      {isSecondary &&
        <StaticImage quality={100} className= 'w-16 h-auto' src = '../../images/svg/grading_secondary.svg' alt = 'Grading Icon' />
      }
     {!isSecondary &&
        <StaticImage quality={100} className= 'w-16 h-auto' src = '../../images/svg/grading_primary.svg' alt = 'Grading Icon' />
      }
    </div>
  )
};

export const GraderIcon = ({isSecondary = false, primaryPath, secondaryPath}) => {
  return (
    <div>
      {isSecondary &&
      <StaticImage quality={100} className= 'w-16 h-auto' src = '../../images/svg/grader_secondary.svg' alt = 'Grading Icon' />
      }
      {!isSecondary &&
      <StaticImage quality={100} className= 'w-16 h-auto' src = '../../images/svg/grader_primary.svg' alt = 'Grading Icon' />
      }
    </div>
  )
};

export const SubmissionIcon = ({isSecondary = false, primaryPath, secondaryPath}) => {
  return (
    <div>
      {isSecondary &&
      <StaticImage quality={100} className= 'w-16 h-auto' src = '../../images/svg/submission_secondary.svg' alt = 'Grading Icon' />
      }
      {!isSecondary &&
      <StaticImage quality={100} className= 'w-16 h-auto' src = '../../images/svg/submission_primary.svg' alt = 'Grading Icon' />
      }
    </div>
  )
};

export const CustomIcon = ({isSecondary = false, primaryPath, secondaryPath}) => {
  return (
    <div>
      {isSecondary &&
      <StaticImage quality={100} className= 'w-16 h-auto' src = '../../images/svg/custom_secondary.svg' alt = 'Grading Icon' />
      }
      {!isSecondary &&
      <StaticImage quality={100} className= 'w-16 h-auto' src = '../../images/svg/custom_primary.svg' alt = 'Grading Icon' />
      }
    </div>
  )
};

export const VirtualIcon = ({isSecondary = false, primaryPath, secondaryPath}) => {
  return (
    <div>
      {isSecondary &&
      <StaticImage quality={100} className= 'w-16 h-auto' src = '../../images/svg/virtual_secondary.svg' alt = 'Grading Icon' />
      }
      {!isSecondary &&
      <StaticImage quality={100} className= 'w-16 h-auto' src = '../../images/svg/virtual_primary.svg' alt = 'Grading Icon' />
      }
    </div>
  )
};

export const ManagementIcon = ({isSecondary = false, primaryPath, secondaryPath}) => {
  return (
    <div>
      {isSecondary &&
      <StaticImage quality={100} className= 'w-16 h-auto' src = '../../images/svg/management_secondary.svg' alt = 'Grading Icon' />
      }
      {!isSecondary &&
      <StaticImage quality={100} className= 'w-16 h-auto' src = '../../images/svg/management_primary.svg' alt = 'Grading Icon' />
      }
    </div>
  )
};
