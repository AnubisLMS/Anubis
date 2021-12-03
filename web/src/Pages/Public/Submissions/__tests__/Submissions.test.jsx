import React from 'react';
import Submissions from '../Submissions';
import {getWrapper} from '../../../../Utils/unitTestHelper';


describe('Basic and Shallow Mount Test Submissions Component', () => {
  it('Basic Render Submissions Component', ()=>{
    const wrapper = getWrapper(<Submissions/>);
    expect(wrapper).toMatchSnapshot();
  });
});
