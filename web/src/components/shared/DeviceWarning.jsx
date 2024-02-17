import React from 'react';
import {browserName, isChrome, isEdgeChromium, isDesktop, isFirefox, isTablet} from 'react-device-detect';
import {useSnackbar} from 'notistack';

export default function DeviceWarning() {
  const {enqueueSnackbar} = useSnackbar();

  React.useEffect(() => {
    const acceptDevice = isDesktop || isTablet;
    const acceptBrowser = isChrome || isFirefox || isEdgeChromium;
    if (!acceptBrowser) {
      enqueueSnackbar(`We noticed you are on ${browserName}. ` +
        'Some things may not work as intended. ' +
        'Try Firefox, Chrome or Edge if you run into any issues!', {variant: 'warning'});
      return;
    }
    if (!acceptDevice) {
      enqueueSnackbar('The Anubis website may not work well ' +
        'outside of a desktop or tablet browser!', {variant: 'warning'});
    }
  }, []);

  return null;
}
