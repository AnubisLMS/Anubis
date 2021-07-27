
import * as React from "react"
import PropTypes from "prop-types"
import {Header} from './';
import {Fade} from './atoms';

const Layout = ({ children }) => {
  return (
    <div className={`flex w-screen flex-col min-h-screen items-center bg-secondary text-white  pb-4 `}>
        <div className= 'absolute w-screen top-0 bg-primary h-2' />
        <div className= 'max-w-5xl w-full flex flex-row justify-center items-center'>
          <Header/>
        </div>
        <div className= {`h-full w-full flex flex-col items-center   space-y-6`}>
            {children}
        </div>
    </div>
  )
}

Layout.propTypes = {
  children: PropTypes.node.isRequired,
}

export default Layout;