select u.netid as uid, at.name as atid, s.created as created
       from assignment_test at
       join assignment a on a.id = at.assignment_id
       join submission_test_result str on at.id = str.assignment_test_id
       join submission s on str.submission_id = s.id
       join user u on u.id = s.owner_id
       where a.name = 'midterm' and str.passed = 1
       group by at.name, u.id
       having min(s.created);
