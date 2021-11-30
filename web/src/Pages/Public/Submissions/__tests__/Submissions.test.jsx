import React from 'react';
import {shallow} from 'enzyme';
import Submissions from '../Submissions';
import renderer from 'react-test-renderer';
import theme from '../../../../Theme/Theme';
import {ThemeProvider} from '@material-ui/core/styles';


describe('Basic and Shallow Mount Test Submissions Component', () => {
  it('Basic Render Submissions Component', ()=>{
    const wrapper = renderer.create(
      <ThemeProvider theme={theme}>
        <Submissions/>
      </ThemeProvider>).toJSON();
    expect(wrapper).toMatchSnapshot();
  });
  it('Shallow render Submissions Component', () => {
    const wrapper = shallow(
      <ThemeProvider theme={theme}>
        <Submissions/>
      </ThemeProvider>);
    expect(wrapper).toMatchSnapshot();
  });
});
