import React from 'react';
import Submission from '../Submission';
import {getWrapper} from '../../../../Utils/unitTestHelper';


describe('Basic and Shallow Mount Test Submission Component', () => {
  it('Basic Render Submission Component', ()=>{
    const wrapper = getWrapper(<Submission/>);
    expect(wrapper).toMatchSnapshot();
  });
});
