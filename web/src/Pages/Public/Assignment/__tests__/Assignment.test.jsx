import React from 'react';
import {shallow} from 'enzyme';
import Assignment from '../Assignment';
import renderer from 'react-test-renderer';
import theme from '../../../../Theme/Dark';
import {ThemeProvider} from '@material-ui/core/styles';
import {MuiThemeProvider} from '@material-ui/core';
import StandardLayout from '../../../../Components/Layouts/StandardLayout';


describe('Basic and Shallow Mount Test of App', () => {
  it('Basic Render Course Component', ()=>{
    const wrapper = renderer.create(
      <ThemeProvider theme={theme}>
        <Assignment/>
      </ThemeProvider>).toJSON();
    expect(wrapper).toMatchSnapshot();
  });
  it('Shallow render Course Component', () => {
    const wrapper = shallow(<Assignment/>);
    expect(wrapper).toMatchSnapshot();
  });
});
