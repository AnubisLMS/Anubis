time_to_pass_test_sql = """
select 
    at.name as assignment_test, 
    u.netid as netid, 
    TIMEDIFF(first_pass.created, first_sub.created) as time_to_pass
from submission_test_result str
         join assignment_test at on str.assignment_test_id = at.id
         join assignment a on at.assignment_id = a.id
         join submission s on s.id = str.submission_id
         join user u on s.owner_id = u.id
         join (
    /* first submissions where it passed */
    select s.id as sid, u.id as uid, at.id as atid, s.created as created
    from assignment_test at
             join assignment a on a.id = at.assignment_id
             join submission_test_result str on at.id = str.assignment_test_id
             join submission s on str.submission_id = s.id
             join user u on u.id = s.owner_id
    where str.passed = 1 and a.id = :assignment_id and at.id = :assignment_test_id
    group by at.name, u.id
    having min(s.created)
) first_pass on first_pass.uid = u.id and first_pass.atid = at.id
        join (
    /* first submissions */
    select s.id as sid, u.id as uid, at.id as atid, s.created as created
    from submission s
             join assignment a on a.id = s.assignment_id
             join user u on u.id = s.owner_id
             join assignment_test at on at.assignment_id = a.id
             join submission_test_result str on str.submission_id = s.id
    where a.id = :assignment_id and at.id = :assignment_test_id
    group by at.name, u.id
    having min(s.created)
) first_sub on first_sub.uid = u.id and first_sub.atid = at.id
where a.id = :assignment_id and at.id = :assignment_test_id
group by at.name, u.id
order by time_to_pass;
"""

assignment_test_pass_count_sql = """
select sum(n)
from (select 1 as n
      from submission_test_result str
               join assignment_test at on str.assignment_test_id = at.id
               join submission s2 on str.submission_id = s2.id
               join assignment a on s2.assignment_id = a.id
               join user u on s2.owner_id = u.id
      where at.id = :assignment_test_id
      group by u.id
      having sum(str.passed) > 0) a
"""

assignment_test_fail_count_sql = """
select sum(n)
from (select 1 as n
      from submission_test_result str
               join assignment_test at on str.assignment_test_id = at.id
               join submission s2 on str.submission_id = s2.id
               join assignment a on s2.assignment_id = a.id
               join user u on s2.owner_id = u.id
      where at.id = :assignment_test_id
      group by u.id
      having sum(str.passed) = 0) a
"""

assignment_test_fail_nosub_sql = """
select sum(n)
from (select 1 as n
      from user u
               where u.id not in (
          select u2.id as uid
          from submission s
                   join user u2 on s.owner_id = u2.id
                   join assignment a2 on s.assignment_id = a2.id
          where a2.id = :assignment_id
      )
      group by u.id) a;
"""
