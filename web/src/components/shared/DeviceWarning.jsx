import React from 'react';
import {browserName, isChrome, isDesktop, isFirefox, isTablet} from 'react-device-detect';
import {useSnackbar} from 'notistack';

export default function DeviceWarning() {
  const {enqueueSnackbar} = useSnackbar();

  React.useEffect(() => {
    const acceptDevice = isDesktop || isTablet;
    const acceptBrowser = isChrome || isFirefox;
    if (!acceptBrowser) {
      enqueueSnackbar(`We noticed you are on ${browserName}. ` +
        'Some things may not work as intended. ' +
        'Try Firefox or Chrome if you run into any issues!', {variant: 'warning'});
      return;
    }
    if (!acceptDevice) {
      enqueueSnackbar('The Anubis website may not work well ' +
        'outside of a desktop or tablet browser!', {variant: 'warning'});
    }
  }, []);

  return null;
}
