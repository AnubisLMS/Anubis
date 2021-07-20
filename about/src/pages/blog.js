import React from 'react';
import {Layout} from '../components';
import { Link, graphql } from "gatsby"
import { FiArrowRight } from "react-icons/fi";
import { motion } from 'framer-motion';

const PostItem = ({title, description, date, author, slug}) => {

  const arrowButtonVariant = {
    hover: {
      opacity: 1,
    },
    initial: {
      opacity: 0,
    },
  }

  return (
    <motion.li
      className='flex flex-row bg-light-600  pt-4 pb-4 pr-6 pl-6 rounded-lg w-full items-center space-x-10  justify-between cursor-pointer  '
      layout initial="initial" whileHover="hover">
      <div className='flex flex-col space-y-2 items-start'>
        <p className='text-xl text-light-100'>{title}</p>
        <p className='text-sm text-light-400'>Posted by {author} on {date}</p>
      </div>
      <motion.div variants = {arrowButtonVariant} transition={{duration: 0.25}}>
        <FiArrowRight className='w-6 h-auto' />
      </motion.div>
    </motion.li>
  )
}

const PostList = ({posts}) => (
  <div className= 'flex col-span-3 flex-col w-full items-center  space-y-8'>
    {posts.map(({frontmatter}, index) => (
      <PostItem {... frontmatter} />
    ))}
  </div>
)

const Blog = ({data}) => {
  const posts = data.allMdx.nodes;
  return (
    <Layout>
      {/*<div className= 'w-full border-2 border-light-100' />*/}
      <div className= 'flex flex-col max-w-5xl w-full items-start justify-center  space-y-24 inline'>
          <h1 className= 'text-6xl font-gosha w-full'>~ Blog</h1>
          <div className= 'w-full'>
            <PostList posts={posts} />
          </div>
      </div>
    </Layout>
  )
};

export default Blog;

export const pageQuery = graphql`
  query {
        site {
            siteMetadata {
                title
                description
            }
        }
        allMdx(
            sort: { fields: [frontmatter___date], order: DESC }
            filter: { frontmatter: { published: { eq: true } } }
        ) {
            nodes {
                id
                excerpt(pruneLength: 250)
                frontmatter {
                    title
                    date
                    author
                    description
                }
            }
        }
  }
`