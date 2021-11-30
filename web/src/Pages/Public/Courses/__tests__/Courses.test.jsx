import React from 'react';
import {shallow} from 'enzyme';
import Courses from '../Courses';
import renderer from 'react-test-renderer';
import theme from '../../../../Theme/Theme';
import {ThemeProvider} from '@material-ui/core/styles';


describe('Basic and Shallow Mount Test Courses Component', () => {
  it('Basic Render Courses Component', ()=>{
    const wrapper = renderer.create(
      <ThemeProvider theme={theme}>
        <Courses/>
      </ThemeProvider>).toJSON();
    expect(wrapper).toMatchSnapshot();
  });
  it('Shallow render Courses Component', () => {
    const wrapper = shallow(
      <ThemeProvider theme={theme}>
        <Courses/>
      </ThemeProvider>);
    expect(wrapper).toMatchSnapshot();
  });
});
