import React from 'react';
import Assignment from '../Assignment';
import {getWrapper} from '../../../../Utils/unitTestHelper';


describe('Basic and Shallow Mount Test Assignment Component', () => {
  it('Basic Render Assignment Component', ()=>{
    const wrapper = getWrapper(<Assignment/>);
    expect(wrapper).toMatchSnapshot();
  });
});
