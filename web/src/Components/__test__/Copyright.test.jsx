import React from 'react';
import {mount, shallow} from 'enzyme';
import Copyright from '../Copyright';

const wrapper = mount(<Copyright/>);
const shallowWrapper = shallow(<Copyright/>);

describe('Shallow and Mount Test of Copyright', () => {
  it('should render the App correctly', () => {
    expect(wrapper).toMatchSnapshot();
  });
  it('should render the App correctly', () => {
    expect(shallowWrapper).toMatchSnapshot();
  });
});
