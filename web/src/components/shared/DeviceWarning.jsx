import React from 'react';
import {browserName, isBrowser, isChrome, isFirefox} from 'react-device-detect';
import {useSnackbar} from 'notistack';

export default function DeviceWarning() {
  const {enqueueSnackbar} = useSnackbar();

  React.useEffect(() => {
    if ((isChrome || isFirefox) && isBrowser) {
      return;
    }

    if (!(isChrome || isFirefox)) {
      enqueueSnackbar(`We noticed you are on ${browserName}. ` +
        'Some things may not work as intended. ' +
        'Try Firefox or Chrome if you run into any issues!', {variant: 'warning'});
      return;
    }

    if (!isBrowser) {
      enqueueSnackbar('The Anubis website may not work well ' +
        'outside of a desktop browser!', {variant: 'warning'});
    }
  }, []);

  return null;
}
