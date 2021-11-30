import React from 'react';
import {shallow} from 'enzyme';
import Assignment from '../Assignment';
import renderer from 'react-test-renderer';
import theme from '../../../../Theme/Theme';
import {ThemeProvider} from '@material-ui/core/styles';


describe('Basic and Shallow Mount Test Assignment Component', () => {
  it('Basic Render Assignment Component', ()=>{
    const wrapper = renderer.create(
      <ThemeProvider theme={theme}>
        <Assignment/>
      </ThemeProvider>).toJSON();
    expect(wrapper).toMatchSnapshot();
  });
  it('Shallow render Assignment Component', () => {
    const wrapper = shallow(
      <ThemeProvider theme={theme}>
        <Assignment/>
      </ThemeProvider>);
    expect(wrapper).toMatchSnapshot();
  });
});
