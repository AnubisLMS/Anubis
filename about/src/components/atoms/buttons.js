import tw from 'twin.macro';
import React from 'react';

//Base Button
const Button = tw.button`text-white pt-2 pb-2 pr-4 pl-4 border-b-2 border-transparent hover:border-primary`;

//Primary Button Variation
export const PrimaryButton = ({children}) => (
  <Button className= 'bg-primary hover:bg-transparent border-2 border-primary'>{children}</Button>
)

//Secondary Button Variation
export const SecondaryButton = ({children}) => (
  <Button className= 'bg-transparent hover:bg-primary border-primary border-2'>{children}</Button>
)

export default Button;