import React from 'react';
import tw from 'twin.macro';
import {Link as GatsbyLink} from 'gatsby';

//Base Link Component
export const Link = tw(GatsbyLink)`hover:text-primary cursor-pointer`;

//Link component for Header
export const HeaderLink = ({children, to = '/'}) => (
  <Link to = {to}  activeClassName = 'text-primary'>{children}</Link>
);

export default Link;