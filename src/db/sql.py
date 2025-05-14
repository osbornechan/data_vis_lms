GET_VALID_LOGIN = """
  SELECT users.user_id, users.user_name FROM users
  INNER JOIN login ON login.user_id = users.user_id
  INNER JOIN enrollment ON enrollment.user_id = users.user_id
  WHERE login.user_login_id = ?
  AND users.user_state = 'registered'
  AND enrollment.enrollment_type = 'teacher'
"""

GET_ALL_USERS = """
  SELECT
    user_name AS Username,
    user_state AS State
  FROM users
  ORDER BY user_id
"""

GET_ALL_COURSES = """
  SELECT
    courses.course_code AS "Course Code",
    courses.course_name AS "Course Name",
    courses.semester AS Semester,
    MAX(CASE 
      WHEN enrollment.enrollment_type = 'teacher' 
      THEN users.user_name 
    END) AS "Instructor",
    COUNT(CASE 
      WHEN enrollment.enrollment_state = 'active'
      AND enrollment.enrollment_type = 'student'
      THEN 1
    END) AS "# of Enrolled Students"
  FROM courses
  INNER JOIN enrollment ON enrollment.course_id = courses.course_id
  INNER JOIN users ON users.user_id = enrollment.user_id
  GROUP BY courses.course_id, courses.course_code, courses.course_name, courses.semester
  ORDER BY courses.semester
"""

GET_ALL_INSTRUCTOR_COURSES = """
  SELECT
    courses.course_code AS "Course Code",
    courses.course_name AS "Course Name",
    courses.semester AS Semester,
    MAX(CASE 
      WHEN enrollment.enrollment_type = 'teacher' 
      THEN users.user_name 
    END) AS "Instructor",
    COUNT(CASE 
      WHEN enrollment.enrollment_state = 'active'
      AND enrollment.enrollment_type = 'student'
      THEN 1
    END) AS "# of Enrolled Students"
  FROM courses
  INNER JOIN enrollment ON enrollment.course_id = courses.course_id
  INNER JOIN users ON users.user_id = enrollment.user_id
  WHERE courses.course_id IN (
    SELECT course_id
    FROM enrollment
    WHERE user_id = ? AND enrollment_type = 'teacher'
  )
  GROUP BY courses.course_id, courses.course_code, courses.course_name, courses.semester
  ORDER BY courses.semester
"""

GET_ENROLLMENT_BY_COURSE = """
  SELECT
    users.user_name AS Username,
    enrollment.enrollment_type AS "Enrollment Type"
  FROM users
  INNER JOIN enrollment ON enrollment.user_id = users.user_id
  WHERE enrollment.course_id = (
    SELECT course_id FROM courses
    WHERE course_code = ?
  )
  AND enrollment_type = 'student'
  ORDER BY enrollment.enrollment_type DESC
"""

GET_ALL_TOPICS = """
  SELECT
    topics.topic_title AS Title,
    topics.topic_content AS Content,
    topics.topic_created_at AS "Created At",
    topics.topic_state AS State,
    courses.course_name AS "Course Name",
    users.user_name AS Author,
    COUNT(CASE 
      WHEN entries.entry_state = 'active'
      AND entries.topic_id = topics.topic_id
      THEN 1
    END) AS "# of Active Entries"
  FROM topics
  INNER JOIN courses ON courses.course_id = topics.course_id
  INNER JOIN users ON users.user_id = topics.topic_posted_by_user_id
  INNER JOIN entries ON entries.topic_id = topics.topic_id
  GROUP BY topics.topic_title, topics.topic_content, topics.topic_created_at, topics.topic_state, courses.course_name, users.user_name
  ORDER BY topics.topic_title
"""

GET_ALL_INSTRUCTOR_TOPICS = """
  SELECT
    topics.topic_title AS Title,
    topics.topic_content AS Content,
    topics.topic_created_at AS "Created At",
    topics.topic_state AS State,
    courses.course_name AS "Course Name",
    users.user_name AS Author,
    COUNT(CASE 
      WHEN entries.entry_state = 'active'
      AND entries.topic_id = topics.topic_id
      THEN 1
    END) AS "# of Active Entries"
  FROM topics
  INNER JOIN courses ON courses.course_id = topics.course_id
  INNER JOIN users ON users.user_id = topics.topic_posted_by_user_id
  INNER JOIN entries ON entries.topic_id = topics.topic_id
  WHERE topics.topic_posted_by_user_id = ?
  GROUP BY topics.topic_title, topics.topic_content, topics.topic_created_at, topics.topic_state, courses.course_name, users.user_name
  ORDER BY topics.topic_title
"""

GET_ALL_ENTRIES = """
  SELECT
    topics.topic_title AS "Topic Title",
    entries.entry_content AS Content,
    users.user_name AS "Entry Author",
    enrollment.enrollment_type AS "Author Type",
    entries.entry_created_at AS "Created At",
  FROM entries
  INNER JOIN users ON users.user_id = entries.entry_posted_by_user_id
  INNER JOIN topics ON topics.topic_id = entries.topic_id
  INNER JOIN enrollment ON enrollment.user_id = entries.entry_posted_by_user_id
  WHERE entries.entry_state = 'active'
"""

GET_ALL_INSTRUCTOR_ENTRIES = """
  SELECT
    topics.topic_title AS "Topic Title",
    entries.entry_content AS Content,
    users.user_name AS "Entry Author",
    enrollment.enrollment_type AS "Author Type",
    entries.entry_created_at AS "Created At",
  FROM entries
  INNER JOIN users ON users.user_id = entries.entry_posted_by_user_id
  INNER JOIN topics ON topics.topic_id = entries.topic_id
  INNER JOIN enrollment ON enrollment.user_id = entries.entry_posted_by_user_id
  WHERE entries.entry_state = 'active'
  AND topics.course_id = (
    SELECT course_id FROM enrollment
    WHERE enrollment.user_id = ?
  )
"""

GET_COURSE_ENTRIES_COUNT_PER_STUDENT = """
  SELECT
    users.user_name AS Username,
    COUNT(CASE 
      WHEN entries.entry_state = 'active'
      AND entries.topic_id = topics.topic_id
      THEN 1
    END) AS "# of Active Entries",
    ROUND(
      100.0 * COUNT(CASE 
        WHEN entries.entry_state = 'active'
        AND entries.topic_id = topics.topic_id
        THEN 1
      END) / SUM(COUNT(CASE 
        WHEN entries.entry_state = 'active'
        AND entries.topic_id = topics.topic_id
        THEN 1
      END)) OVER (), 
      2
    ) AS "% Participation"
  FROM entries
  INNER JOIN users ON users.user_id = entries.entry_posted_by_user_id
  INNER JOIN topics ON topics.topic_id = entries.topic_id
  INNER JOIN enrollment ON enrollment.user_id = entries.entry_posted_by_user_id
  WHERE enrollment.enrollment_type = 'student'
  AND enrollment.course_id = (
    SELECT course_id FROM enrollment
    WHERE enrollment.user_id = ?
  )
  GROUP BY users.user_name
  ORDER BY "# of Active Entries" DESC
"""

GET_ALL_ENTRIES_COUNT_PER_STUDENT = """
  SELECT
    users.user_name AS Username,
    COUNT(CASE 
      WHEN entries.entry_state = 'active'
      AND entries.topic_id = topics.topic_id
      THEN 1
    END) AS "# of Active Entries",
    ROUND(
      100.0 * COUNT(CASE 
        WHEN entries.entry_state = 'active'
        AND entries.topic_id = topics.topic_id
        THEN 1
      END) / SUM(COUNT(CASE 
        WHEN entries.entry_state = 'active'
        AND entries.topic_id = topics.topic_id
        THEN 1
      END)) OVER (), 
      2
    ) AS "% Participation"
  FROM entries
  INNER JOIN users ON users.user_id = entries.entry_posted_by_user_id
  INNER JOIN topics ON topics.topic_id = entries.topic_id
  INNER JOIN enrollment ON enrollment.user_id = entries.entry_posted_by_user_id
  WHERE enrollment.enrollment_type = 'student'
  GROUP BY users.user_name
  ORDER BY "# of Active Entries" DESC
"""



