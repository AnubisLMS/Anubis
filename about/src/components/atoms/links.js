import React from 'react';
import tw from 'twin.macro';
import {Link as GatsbyLink} from 'gatsby';

//Base Link Component
export const Link = tw(GatsbyLink)`text-light-400 hover:text-light-100 cursor-pointer`;

//Link component for Header
export const HeaderLink = ({children, to = '/'}) => (
  <Link to = {to}  activeClassName = 'pb-2 border-b-2 ' className = 'pb-2 hover:border-b-2 hover:border-light-100'>{children}</Link>
);

export default Link;