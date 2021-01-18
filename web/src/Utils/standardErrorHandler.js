export default (enqueueSnackbar) => (error) => {
  enqueueSnackbar(error.toString(), {variant: 'error'});
};
