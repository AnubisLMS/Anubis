import React from 'react';

export default function AboutRedirect({user}) {
  React.useEffect(() => {
    if (user === null) {
      window.location = 'https://anubis-lms.io/';
      window.reload(false);
    }
  }, [user]);
  return null;
}
