import React from 'react';
import useQuery from '../../hooks/useQuery';
import {useSnackbar} from 'notistack';

export default function Error() {
  const {enqueueSnackbar} = useSnackbar();
  const query = useQuery();
  const error = query.get('error');

  React.useEffect(() => {
    if (!error) return undefined;
    enqueueSnackbar(error, {variant: 'error'});
  }, [error]);

  return (
    <div/>
  );
}
