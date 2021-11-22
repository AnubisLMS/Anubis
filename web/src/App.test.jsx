import React from 'react';
import renderer from 'react-test-renderer';
import {shallow} from 'enzyme';
import App from './App';


describe('Basic and Shallow Mount Test of App', () => {
  it('Basic render App Component', () => {
    const wrapper = renderer.create(<App/>).toJSON();
    if (wrapper) {
      expect(wrapper).toMatchSnapshot();
    }
  });
  it('Shallow render App Component', () => {
    const wrapper = shallow(<App/>);
    expect(wrapper).toMatchSnapshot();
  });
});
