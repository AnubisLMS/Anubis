import React from 'react';
import { graphql, Link } from 'gatsby';
import { MDXProvider } from '@mdx-js/react';
import { MDXRenderer } from 'gatsby-plugin-mdx';
import { Layout } from '../';
import {formatDate} from '../../utils/date';

export const pageQuery = graphql`
  query($slug: String!) {
    mdx(fields: { slug: { eq: $slug } }) {
      body
      frontmatter {
        title
        author
        date
      }
    }
  }
`;

const Post = ({ data }) => {
  const { frontmatter, body } = data.mdx;
  console.log(data);
  return (
    <Layout>
      <div className="flex flex-col max-w-5xl w-full items-start justify-center space-y-8 inline pt-20 pl-4 pr-4">
        <h1 className="text-4xl  font-gosha w-full">
          <span className="text-primary">~ </span>
          {frontmatter.title}
        </h1>
        <div className="bg-light-600 p-4 w-full rounded-lg flex flex-row space-x-6">
          <p className="text-light-200">
            Posted By:{' '}
            <span className="text-light-300 "> {frontmatter.author}</span>
          </p>
          <p className="text-light-200 space-x-4">
            Date: <span className="text-light-300">{formatDate(frontmatter.date)}</span>
          </p>
        </div>
        <div className="space-y-8 pl-4 pr-4 pb-20">
          <MDXProvider
            components={{
              h4: ({ children }) => (
                <h4 className="text-xl text-light-200 border-b-2 border-primary pb-2 inline-block pt-8">
                  {children}
                </h4>
              ),
              p: ({ children }) => (
                <p className="text-md text-light-300">{children}</p>
              ),
              li: ({ children }) => (
                <li className="text-md text-light-300">
                  <span className="text-primary text-lg">· </span>
                  {children}
                </li>
              ),
              blockquote: ({ children }) => (
                <p className="bg-light-600 p-4 border-l-2 border-primary w-full">
                  {children}
                </p>
              ),
              code: ({ children }) => <p>{children}</p>,
            }}
          >
            <MDXRenderer>{body}</MDXRenderer>
          </MDXProvider>
        </div>
      </div>
    </Layout>
  );
};

export default Post;
