
import * as React from "react"
import PropTypes from "prop-types"
import {Header} from './';

const Layout = ({ children, isCentered = false }) => {
  return (
    <div className={`flex flex-col h-screen ${isCentered ? 'h-screen' : 'min-h-screen'} bg-secondary text-white bg-swirl bg-cover`}>
      <div className= 'w-full p-4'>
        <Header/>
      </div>
      <div className= {`h-full w-full flex flex-col items-center  p-4 ${isCentered ? 'mb-20 justify-center' : 'mt-20'} space-y-6`}>
        {children}
      </div>
    </div>
  )
}

Layout.propTypes = {
  children: PropTypes.node.isRequired,
}

export default Layout;
