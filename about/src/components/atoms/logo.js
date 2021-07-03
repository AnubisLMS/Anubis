import React from 'react';

import {StaticImage} from "gatsby-plugin-image";
import {Link} from 'gatsby';

//Logo with href to home
const Logo = () => (
  <Link to = '/'>
    <StaticImage className = 'h-auto w-40 hover:opacity-50 cursor-pointer' src={'../../images/logo.png'} quality={100} alt={'Anubis Logo'}/>
  </Link>
);

export default Logo;