select
  aq.sequence as 'question number',
  aq.last_updated as last_updated,
  asq.response as response
  from assigned_student_question asq
         join assignment a on a.id = asq.assignment_id
         join user u on asq.owner_id = u.id
         join assignment_question aq on aq.id = asq.question_id
 where u.netid = 'ai1138' and a.name = 'midterm'
       order by aq.sequence;
