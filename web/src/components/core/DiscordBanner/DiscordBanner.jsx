import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import GenericAd from '../../shared/Ad/GenericAd/GenericAd';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../utils/standardStatusHandler';


export default function DiscordBanner() {
  const [discordInfo, setDiscordInfo] = useState(null);
  const {enqueueSnackbar} = useSnackbar();


  useEffect(() => {
    axios.get('/api/public/info/discord').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setDiscordInfo(data);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  if (discordInfo === null || Object.keys(discordInfo).length === 0) {
    return null;
  }

  return (
    <GenericAd data={discordInfo}/>
  );
}
