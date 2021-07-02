import React from 'react';

import {StaticImage} from "gatsby-plugin-image";


const Logo = () => (
  <StaticImage className = 'h-auto w-40' src={'../../images/logo.png'} quality={100} alt={'Anubis Logo'}/>
);

export default Logo;