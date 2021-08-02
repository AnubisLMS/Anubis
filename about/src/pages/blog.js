import React from 'react';
import { Layout } from '../components';
import { Link, graphql, navigate } from 'gatsby';
import { FiArrowRight } from 'react-icons/fi';
import { motion } from 'framer-motion';
import {formatDate} from '../utils/date';

const PostItem = ({ title, description, date, author, slug }) => {
  const arrowButtonVariant = {
    hover: {
      opacity: 1,
    },
    initial: {
      opacity: 0,
    },
  };

  const parentVariant = {
    hover: {
      scale: 1.04,
    },
  };

  return (
    <motion.li
      onClick={() => navigate(slug)}
      variants={parentVariant}
      className="flex flex-row bg-light-600  pt-4 pb-4 pr-6 pl-6 rounded-lg w-full items-center space-x-10  justify-between cursor-pointer  "
      layout
      initial="initial"
      whileHover="hover"
    >
      <div className="flex flex-col space-y-2 items-start">
        <div className="flex flex-row items-center justify-between space-x-6">
          <p className="text-xl text-light-100">{title}</p>
        </div>
        <p className="text-light-400">{description.substr(0, 120)}...</p>
        <p className="text-sm text-light-500">
          Posted by {author} on {formatDate(date)}
        </p>
      </div>
      <motion.div variants={arrowButtonVariant} transition={{ duration: 0.25 }}>
        <FiArrowRight className="w-6 h-auto" />
      </motion.div>
    </motion.li>
  );
};

const PostList = ({ posts }) => (
  <div className="flex col-span-3 flex-col w-full items-center  space-y-8">
    {posts.map(({ frontmatter, fields }, index) => (
      <PostItem {...frontmatter} {...fields} />
    ))}
  </div>
);

const Blog = ({ data }) => {
  const posts = data.allMdx.nodes;
  return (
    <Layout>
      <div className="flex flex-col max-w-5xl w-full items-start justify-center  space-y-24 inline pt-20">
        <h1 className="text-6xl font-gosha w-full">
          <span className="text-primary">~</span> Blog
        </h1>
        <div className="w-full">
          <PostList posts={posts} />
        </div>
      </div>
    </Layout>
  );
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
        fields {
          slug
        }
      }
    }
  }
`;
