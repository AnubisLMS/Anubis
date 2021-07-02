import * as React from "react"
import {Layout} from '../components'
import {PrimaryButton, SecondaryButton} from "../components/atoms";

export const Home = () => {
  return (
    <Layout isLandingPage>
      <div className= 'flex flex-col max-w-4xl items-center justify-center text-center space-y-10'>
        <h1 className= 'text-8xl'>Completely Automate your CS Course</h1>
        <div className= 'space-x-4'>
          <PrimaryButton>Request A Demo</PrimaryButton>
          <SecondaryButton>Learn More</SecondaryButton>
        </div>
      </div>
    </Layout>
  )
}

export default Home;

