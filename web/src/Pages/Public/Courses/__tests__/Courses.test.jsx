import React from 'react';
import {shallow} from 'enzyme';
import Courses from '../Courses';
import renderer from 'react-test-renderer';
import theme from '../../../../Theme/Dark';
import {ThemeProvider} from '@material-ui/core/styles';


describe('Basic and Shallow Mount Test of App', () => {
  it('Basic Render Course Component', ()=>{
    const wrapper = renderer.create(
      <ThemeProvider theme={theme}>
        <Courses/>
      </ThemeProvider>).toJSON();
    expect(wrapper).toMatchSnapshot();
  });
  it('Shallow render Course Component', () => {
    const wrapper = shallow(<Courses/>);
    expect(wrapper).toMatchSnapshot();
  });
});
