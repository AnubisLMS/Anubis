import React from 'react';
import Box from '@mui/material/Box';
import useTheme from '@mui/material/styles/useTheme';

import StandardLayout from '../../../components/shared/Layouts/StandardLayout';
import PrivacyPolicyText from '../../../components/shared/PrivacyPolicy/PrivacyPolicy';
import SectionHeader from '../../../components/shared/SectionHeader/SectionHeader';

export default function PrivacyPolicy() {
  const theme = useTheme();
  return (
    <StandardLayout>
      <SectionHeader isPage title='Anubis LMS Privacy Policy'/>
      <Box sx={{
        width: '100%',
        borderTop: `1px solid ${theme.palette.dark.blue['200']}`,
        marginTop: 2,
        height: '1px',
      }}/>
      <PrivacyPolicyText/>
    </StandardLayout>
  );
}
