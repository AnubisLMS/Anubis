import tw from 'twin.macro';
import React from 'react';
import { motion } from 'framer-motion';

//Base Button
const Button = tw(motion.button)`pt-3 pb-3 pr-5 pl-5`;

//Primary Button Variation
export const PrimaryButton = ({ children, onClick }) => (
  <Button
    onClick={onClick}
    whileHover={{ scale: 1.03 }}
    whileTap={{ scale: 0.95 }}
    className="bg-light-200 text-dark rounded-lg hover:bg-light-100 "
  >
    {children}
  </Button>
);

//Secondary Button Variation
export const SecondaryButton = ({ children, onClick }) => (
  <Button
    onClick={onClick}
    className="bg-transparent border-2 border-light-400 rounded-lg hover:border-light-100 hover:border-4 text-light-400 hover:text-light-100"
    whileHover={{ scale: 1.03 }}
    whileTap={{ scale: 0.95 }}
  >
    {children}
  </Button>
);

export default Button;
