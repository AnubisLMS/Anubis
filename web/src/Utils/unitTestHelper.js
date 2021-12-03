import renderer from 'react-test-renderer';
import {ThemeProvider} from '@material-ui/core/styles';
import theme from '../Theme/Theme';
import {SnackbarProvider} from 'notistack';
import React from 'react';

export const getWrapper = (component) => {
  return renderer.create(
    <ThemeProvider theme={theme}>
      <SnackbarProvider>
        {component}
      </SnackbarProvider>
    </ThemeProvider>,
  ).toJSON();
};
