import React from 'react';
import {shallow} from 'enzyme';
import Submission from '../Submission';
import renderer from 'react-test-renderer';
import theme from '../../../../Theme/Theme';
import {ThemeProvider} from '@material-ui/core/styles';
import {SnackbarProvider} from 'notistack';


describe('Basic and Shallow Mount Test Submission Component', () => {
  it('Basic Render Submission Component', ()=>{
    const wrapper = renderer.create(
      <ThemeProvider theme={theme}>
        <SnackbarProvider>
          <Submission/>
        </SnackbarProvider>
      </ThemeProvider>).toJSON();
    expect(wrapper).toMatchSnapshot();
  });
  it('Shallow render Submission Component', () => {
    const wrapper = shallow(
      <ThemeProvider theme={theme}>
        <Submission/>
      </ThemeProvider>);
    expect(wrapper).toMatchSnapshot();
  });
});
