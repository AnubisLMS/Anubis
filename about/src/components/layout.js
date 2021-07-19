
import * as React from "react"
import PropTypes from "prop-types"
import {Header} from './';
import {Fade} from './atoms';

const Layout = ({ children, isCentered = false }) => {
  return (
    <div className={`flex flex-col ${isCentered ? 'h-screen' : 'min-h-screen'} items-center bg-secondary text-white  pb-4`}>
      <div className= 'max-w-5xl w-full flex flex-row justify-center items-center'>
        <Header/>
      </div>
      <div className= {`h-full w-full flex flex-col items-center  pt-20  pb-20 pl-4 pr-4 ${isCentered ? 'mb-20 justify-center' : 'mt-20'} space-y-6`}>
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