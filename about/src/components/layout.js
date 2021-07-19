
import * as React from "react"
import PropTypes from "prop-types"
import {Header} from './';
import {Fade} from './atoms';

const Layout = ({ children, isCentered = false }) => {
  return (
    <div className={`flex flex-col ${isCentered ? 'h-screen' : 'min-h-screen'} bg-secondary text-white bg-swirl bg-cover pb-4`}>
      <div className= 'w-full p-4'>
        <Header/>
      </div>
      <div className= {`h-full w-full flex flex-col items-center  p-4 ${isCentered ? 'mb-20 justify-center' : 'mt-20'} space-y-6`}>
        <Fade>
          {children}
        </Fade>
      </div>
    </div>
  )
}

Layout.propTypes = {
  children: PropTypes.node.isRequired,
}

export default Layout;