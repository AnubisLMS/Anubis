import React from 'react';
import Course from '../Course';
import {getWrapper} from '../../../../Utils/unitTestHelper';


describe('Basic and Shallow Mount Test Course Component', () => {
  it('Basic Render Course Component', ()=>{
    const wrapper = getWrapper(<Course/>);
    expect(wrapper).toMatchSnapshot();
  });
});
