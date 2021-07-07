import React from 'react';
import tw from 'twin.macro';
import {Link as GatsbyLink} from 'gatsby';

//Base Link Component
export const Link = tw(GatsbyLink)`hover:text-primary cursor-pointer`;

//Link component for Header
export const HeaderLink = ({children, to = '/'}) => (
  <Link to = {to}  activeClassName = 'pb-2 border-b-2 border-primary'>{children}</Link>
);

export default Link;