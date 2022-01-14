export default (enqueueSnackbar) => (error) => {
  if (error.toString().match('status code 401')) {
    window.location = '/api/public/auth/login';
    return;
  }
  enqueueSnackbar(error.toString(), {variant: 'error'});
};
