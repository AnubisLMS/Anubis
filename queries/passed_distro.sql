select a.name, s.state, count(s.id), st.passed
  from submission s
         join assignment a on a.id = s.assignment_id
         join (
           select str.submission_id as submission_id, sum(str.passed) as passed
             from submission_test_result str
            group by str.submission_id
         ) st on st.submission_id = s.id
 where a.name = 'midterm'
 group by s.state, st.passed;
