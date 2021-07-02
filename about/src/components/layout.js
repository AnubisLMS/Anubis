
import * as React from "react"
import PropTypes from "prop-types"
import {Header} from './';
const Layout = ({ children, isLandingPage = false }) => {
  return (
    <div className={`flex flex-col h-screen ${isLandingPage ? 'h-screen' : 'min-h-screen'} bg-secondary text-white bg-swirl bg-cover`}>
      <div className= 'w-full p-4'>
        <Header/>
      </div>
      <div className= {`h-full w-full flex flex-col items-center justify-center p-4 ${isLandingPage ? 'mb-20' : ''}`}>
        {children}
      </div>
    </div>
  )
}

Layout.propTypes = {
  children: PropTypes.node.isRequired,
}

export default Layout;
