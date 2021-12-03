import React from 'react';
import Courses from '../Courses';
import {getWrapper} from '../../../../Utils/unitTestHelper';


describe('Basic and Shallow Mount Test Courses Component', () => {
  it('Basic Render Courses Component', ()=>{
    const wrapper = getWrapper(<Courses/>);
    expect(wrapper).toMatchSnapshot();
  });
});
