import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

export default function PrivacyPolicy() {
  return (
    <Box sx={{m: 2}}>
      <Typography variant={'body2'}>
        By using this application, you are agreeing to be bound by the terms and conditions of this agreement.
        If you do not agree to the terms of this agreement, do not use the application. This agreement is a legal
        document between you and the company
        and it governs your use of the application made available to you by the company. This agreement is between you
        and the company only and not with the application store. Therefore, the company is solely
        responsible for the application and its content. Although the application store is not a party to this
        agreement, it has the right to enforce it against you as a third party
        beneficiary relating to your use of the application. Since the application can be
        accessed and used by other users via, for example, family sharing/family group or volume purchasing, the use
        of the application by those users is expressly subject to this agreement. The application
        is licensed, not sold to you by the company for use strictly in accordance with the
        terms of this agreement.
      </Typography>
    </Box>
  );
}
