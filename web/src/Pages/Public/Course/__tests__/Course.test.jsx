import React from 'react';
import {shallow} from 'enzyme';
import Course from '../Course';
import renderer from 'react-test-renderer';
import theme from '../../../../Theme/Theme';
import {ThemeProvider} from '@material-ui/core/styles';


describe('Basic and Shallow Mount Test Course Component', () => {
  it('Basic Render Course Component', ()=>{
    const wrapper = renderer.create(
      <ThemeProvider theme={theme}>
        <Course/>
      </ThemeProvider>).toJSON();
    expect(wrapper).toMatchSnapshot();
  });
  it('Shallow render Course Component', () => {
    const wrapper = shallow(
      <ThemeProvider theme={theme}>
        <Course/>
      </ThemeProvider>);
    expect(wrapper).toMatchSnapshot();
  });
});
