import tw from 'twin.macro';
import React from 'react';
import { motion } from 'framer-motion';

//Base Button
const Button = tw(motion.button)`text-white pt-3 pb-3 pr-6 pl-6`;

//Primary Button Variation
export const PrimaryButton = ({children, onClick}) => (
  <Button onClick = {onClick}  whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className= 'bg-primary rounded-lg border-2 border-primary'>{children}</Button>
)

//Secondary Button Variation
export const SecondaryButton = ({children, onClick}) => (
  <Button onClick = {onClick} className= 'bg-transparent  border-primary border-2 rounded-lg' whileHover = {{scale: 1.05}} whileTap = {{scale: .95}}>{children}</Button>
)

export default Button;