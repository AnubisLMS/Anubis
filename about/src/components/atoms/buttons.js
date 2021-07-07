import tw from 'twin.macro';
import React from 'react';

//Base Button
const Button = tw.button`text-white pt-3 pb-3 pr-6 pl-6`;

//Primary Button Variation
export const PrimaryButton = ({children, onClick}) => (
  <Button onClick = {onClick} className= 'bg-primary hover:bg-transparent border-2 border-primary hover:text-white'>{children}</Button>
)

//Secondary Button Variation
export const SecondaryButton = ({children, onClick}) => (
  <Button onClick = {onClick} className= 'bg-transparent hover:bg-primary border-primary border-2 hover:text-white'>{children}</Button>
)

export default Button;