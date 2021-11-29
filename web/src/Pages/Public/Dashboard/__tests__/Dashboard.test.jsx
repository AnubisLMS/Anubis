import React from 'react';
import {shallow} from 'enzyme';
import Dashboard from '../Dashboard';
import renderer from 'react-test-renderer';
import theme from '../../../../Theme/Dark';
import {ThemeProvider} from '@material-ui/core/styles';
import {MuiThemeProvider} from '@material-ui/core';
import StandardLayout from '../../../../Components/Layouts/StandardLayout';


describe('Basic and Shallow Mount Test Dashboard Component', () => {
  it('Basic Render Dashboard Component', ()=>{
    const wrapper = renderer.create(
      <ThemeProvider theme={theme}>
        <Dashboard/>
      </ThemeProvider>).toJSON();
    expect(wrapper).toMatchSnapshot();
  });
  it('Shallow render Dashboard Component', () => {
    const wrapper = shallow(<Dashboard/>);
    expect(wrapper).toMatchSnapshot();
  });
});
