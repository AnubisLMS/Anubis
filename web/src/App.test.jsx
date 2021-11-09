import React from 'react';
import {mount, shallow} from 'enzyme';
import App from './App';

const wrapper = mount(<App/>);
const shallowWrapper = shallow(<App/>);

describe('Shallow and Mount Test of App', () => {
  it('should render the App correctly', () => {
    expect(wrapper).toMatchSnapshot();
  });
  it('should render the App correctly', () => {
    expect(shallowWrapper).toMatchSnapshot();
  });
});
