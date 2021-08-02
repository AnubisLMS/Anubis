import React, { useState, useEffect } from 'react';
import { Layout } from '../components';
import { FiArrowRight } from 'react-icons/fi';
import { motion } from 'framer-motion';
import { useQuery } from '../hooks/useQuery';
const reasons = [
  'You want to get involved in building Anubis',
  'You are an institution, and are looking to automate your CS Classes',
  'You are a current Anubis user and have an issue or potential feature you want us to know about',
  'You just want to say Hi',
];

const Contact = (props) => {
  const {
    location: { search },
  } = props;
  const query = useQuery(search);

  const [subject, setSubject] = useState('');

  useEffect(() => {
    if (query?.demo) setSubject('Anubis Demo Request');
  }, []);

  return (
    <Layout>
      <div className="flex flex-col max-w-5xl w-full items-start justify-center  space-y-24 inline pt-20">
        <h1 className="text-6xl  font-gosha w-full">
          <span className="text-primary">~</span> Contact
        </h1>
        <div className="w-full bg-light-600 rounded-lg pt-12 pb-12 pr-12 pl-12 space-y-8">
          <h1 className="text-2xl font-bold w-3/4">
            Get a behind the scenes look at what we are currently learning,
            exploring, and creating.
          </h1>
          <p className="text-lg text-light-300">
            Reasons why you should reach out:{' '}
          </p>
          <div className="flex flex-col space-y-4">
            {reasons.map((reason, index) => (
              <div
                key={`${index}-${reason}`}
                className="flex flex-row items-center space-x-4"
              >
                <FiArrowRight className="text-primary text-xl" />
                <p className="text-lg">{reason}</p>
              </div>
            ))}
          </div>
          <div className="relative w-5/6">
            <input
              className="bg-light-500 pt-3 pb-3 pl-4 pr-4 border-2 border-primary rounded-lg w-full text-light-100"
              value={subject}
              onChange={(event) => setSubject(event.target.value)}
              placeholder="Email Subject"
            />
            <motion.a
              whileHover={{ scale: 1.1 }}
              className="absolute right-0 bg-primary rounded-lg h-full pr-6 pl-6 leading-loose text-center pt-2 cursor-pointer"
              href={`mailto:anubis@osiris.cyber.nyu.edu?subject=${subject}`}
            >
              Send!
            </motion.a>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Contact;
