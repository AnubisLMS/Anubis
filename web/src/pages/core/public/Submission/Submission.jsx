import React from 'react';
import {useParams} from 'react-router-dom';
import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import SubmissionTests from '../../../../components/core/Submission/SubmissionTests';


export default function Submission() {
  const {submissionId} = useParams();

  return (
    <StandardLayout>
      <SubmissionTests submissionId={submissionId}/>
    </StandardLayout>
  );
}

