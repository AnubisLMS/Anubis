import React from 'react';
import tw from 'twin.macro';
import { Link as GatsbyLink } from 'gatsby';

//Base Link Component
export const Link = tw(GatsbyLink)` cursor-pointer`;

//Link component for Header
export const HeaderLink = ({ children, to = '/' }) => (
  <Link
    to={to}
    activeClassName="pb-2 border-b-2 text-light-100 border-primary"
    className="text-light-400 pb-2 hover:text-light-200 "
  >
    {children}
  </Link>
);

export default Link;
