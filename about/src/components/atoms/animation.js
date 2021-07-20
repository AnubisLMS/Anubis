import { motion } from 'framer-motion';
import React from 'react';


export const Fade = ({children}) => (
  <motion.div className= 'w-max' transition = {{duration: 2}} initial = {{opacity: 0}} animate = {{opacity: 1}}>
    {children}
  </motion.div>
)
