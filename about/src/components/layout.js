
import * as React from "react"
import PropTypes from "prop-types"
import {Header} from './';
const Layout = ({ children }) => {
  return (
    <div className='h-full min-h-screen w-full bg-secondary text-white'>
      <Header/>
      {children}
    </div>
  )
}

Layout.propTypes = {
  children: PropTypes.node.isRequired,
}

export default Layout
