import React from 'react';
import {shallow} from 'enzyme';
import Dashboard from '../Dashboard';
import renderer from 'react-test-renderer';
import theme from '../../../../Theme/Theme';
import {ThemeProvider} from '@material-ui/core/styles';
import {SnackbarProvider} from 'notistack';


describe('Basic and Shallow Mount Test Dashboard Component', () => {
  it('Basic Render Dashboard Component', ()=>{
    const wrapper = renderer.create(
      <ThemeProvider theme={theme}>
        <SnackbarProvider>
          <Dashboard/>
        </SnackbarProvider>
      </ThemeProvider>).toJSON();
    expect(wrapper).toMatchSnapshot();
  });
  it('Shallow render Dashboard Component', () => {
    const wrapper = shallow(
      <ThemeProvider theme={theme}>
        <Dashboard/>
      </ThemeProvider>);
    expect(wrapper).toMatchSnapshot();
  });
});
