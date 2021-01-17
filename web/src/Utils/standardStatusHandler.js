export default function standardStatusHandler(response, enqueueSnackbar) {
  if (response.status === 200) {
    const status = response?.data?.data?.status;
    const error = response?.data?.error;
    const data = response?.data?.data;
    const variant = response?.data?.data?.variant ?? 'success';

    if (status && typeof status === 'string') {
      enqueueSnackbar(status, {variant});
    }

    if (error && typeof error === 'string') {
      enqueueSnackbar(error, {variant: 'error'});
      return null;
    }

    if (data) {
      return data;
    }
  }

  enqueueSnackbar('The api returned a error we don\'t know how to display :(', {variant: 'error'});
  return false;
}
