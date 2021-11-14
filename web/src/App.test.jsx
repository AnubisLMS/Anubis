import React from 'react';
import {shallow} from 'enzyme';
import App from './App';


describe('Shallow Mount Test of App', () => {
  it('Shallow render App Component', () => {
    const wrapper = shallow(<App/>);
    expect(wrapper).toMatchSnapshot();
  });
});
