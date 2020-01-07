# db

### Tables

- submissions - job results (grades
  - id - int
  - timestamp - datetime (job creation time ie. submission time)
  - studentid - string (netid)

- testresults - individual test results
  - id - int
  - submissionid - int (foreign key)
  - grade - int
  - message - string

- events
  - id - int
  - timestamp - datetime
  - type - string
  - message - string
