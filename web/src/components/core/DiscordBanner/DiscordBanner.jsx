import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import GenericAd from '../../shared/Ad/GenericAd/GenericAd';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../utils/standardStatusHandler';


export default function DiscordBanner() {
  const defaultInfo = {
    'severity': 'info',
    'title': 'Anubis Discord',
    'content': 'Anubis was created by a single sophomore just like you, and is now run by students. ' +
      'If you want to grow and work on something more rewarding ' +
      'than your classes join our discord. Challenge yourself to do better.',
    'action': {
      'href': 'https://github.com/AnubisLMS/Anubis',
      'label': 'Anubis Discord',
    },
  };

  console.log(JSON.stringify(defaultInfo));

  const [discordInfo, setDiscordInfo] = useState(defaultInfo);
  const {enqueueSnackbar} = useSnackbar();


  useEffect(() => {
    axios.get('/api/public/info/discord').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data && data.length > 0) {
        setDiscordInfo(data);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  if (discordInfo === null) {
    return null;
  }

  return (
    <GenericAd data={discordInfo}/>
  );
}
