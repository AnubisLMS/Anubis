import React from 'react';
import Dashboard from '../Dashboard';
import {getWrapper} from '../../../../Utils/unitTestHelper';


describe('Basic and Shallow Mount Test Dashboard Component', () => {
  it('Basic Render Dashboard Component', ()=>{
    const wrapper = getWrapper(<Dashboard/>);
    expect(wrapper).toMatchSnapshot();
  });
});
