import tw from 'twin.macro';
import React from 'react';
export const PageTitle = tw.h1`text-4xl font-bold`;

export const ListItem = ({children}) => (
  <li><span className= 'text-primary ml-2 mr-2 font-bold'>-</span>{children}</li>
)

export const Code = tw.div`p-4 bg-gray-800 text-white rounded-md`

export const Highlight = tw.span`p-2 bg-gray-800 rounded-md`