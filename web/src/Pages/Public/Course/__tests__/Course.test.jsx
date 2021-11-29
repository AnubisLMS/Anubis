import React from 'react';
import {render} from '@testing-library/react';
import {shallow} from 'enzyme';
import Course from '../Course';
import renderer from 'react-test-renderer';
import theme from '../../../../Theme/Dark';
import {ThemeProvider} from '@material-ui/core/styles';
import {MuiThemeProvider} from '@material-ui/core';
import StandardLayout from '../../../../Components/Layouts/StandardLayout';


describe('Basic and Shallow Mount Test of App', () => {
  it('Basic Render Course Component', ()=>{
    const wrapper = renderer.create(
      <ThemeProvider theme={theme}>
        <Course/>
      </ThemeProvider>).toJSON();
    expect(wrapper).toMatchSnapshot();
  });
  it('Shallow render Course Component', () => {
    const wrapper = shallow(<Course/>);
    expect(wrapper).toMatchSnapshot();
  });
});
