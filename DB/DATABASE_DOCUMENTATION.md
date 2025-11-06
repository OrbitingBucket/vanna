# Artelia Learning Database Documentation
Generated: 2025-11-06 13:43:56

## Database Overview

**Database Name:** artelia_learning

**Purpose:** Centralized learning and development data warehouse for Artelia Group

**Data Sources:**
- 360Learning (Main LMS platform)
- GoodHabitz (Self-paced microlearning modules)
- GlobalExam (Language learning - SCORM attendance and virtual classes)
- Denmark Classrooms (Physical training sessions)

**Critical Business Rules:**
1. **Active Employees Filter:** `deletion_date IS NULL` - ALWAYS use this unless analyzing historical data
2. **Total Active Employees:** 9,837 (out of 14,163 total users)
3. **Join Keys:**
   - GoodHabitz: `audit_users.user_id = goodhabitz_username`
   - SCORM/GlobalExam: `LOWER(audit_users.email) = LOWER(scorm_email)`
   - 360Learning: `LOWER(audit_users.email) = LOWER(course_email)`
4. **Location Grouping:** `CASE WHEN country = 'France' THEN 'France' ELSE 'International' END`

---

## 1. Table: `audit_users`

**Description:** Master employee table containing all users from 360Learning platform.

**Row Count:** 14,163 total users (9,837 active)

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | integer |  |
| user_id | text | Unique 360Learning user identifier (24-char hex string) |
| email | text | Employee email address (lowercase recommended for joins) |
| first_name | text | Employee first name |
| last_name | text | Employee last name |
| country | text | Employee country (e.g., France, Morocco, USA) |
| company | text | Company name within Artelia Group |
| branch | text | Branch location |
| bu | text | Business Unit code (e.g., BRE, EUR, EAMO, IND, VT, MI, APAC, BMI, BP, NORD, ADS, CAN) |
| place_of_work | text | Work location |
| is_manager | text | Boolean: true if user manages others |
| manager1_name | text | Direct manager name |
| manager2_name | text | Second-level manager name |
| rrh_name | text | HR representative name |
| matricule | text | Employee ID number |
| gender | text | Employee gender |
| start_date | text | Employment start date |
| account_creation_date | text | Date 360Learning account was created |
| shell | boolean | Shell account indicator (true for test/system accounts) |
| user_groups | text | Comma-separated list of user groups |
| all_data | jsonb |  |
| created_at | timestamp without time zone | Record creation timestamp in database |
| deletion_date | text | Date account was deactivated (NULL = active employee) |
| automatic_deletion_date | text | Scheduled deletion date |

### Sample Data

```
user_id: 67a2ff8ead09e7a84ee733d4
email: kheireddine.bouguerra@arteliagroup.com
name: Kheireddine BOUGUERRA
country: Canada
bu: CAN
deletion_date: None

user_id: 661e06806663035a50c428bb
email: khelaf.khales@arteliagroup.com
name: Khelaf KHALES
country: France
bu: BMI
deletion_date: None

user_id: 64e592ace93205e985c7a54c
email: khelifa.zedjar@arteliagroup.com
name: Khélifa ZEDJAR
country: France
bu: BMI
deletion_date: None

```

### Common Queries

**Find active employees:**
```sql
SELECT user_id, email, first_name, last_name, country, bu
FROM audit_users
WHERE deletion_date IS NULL;
```

**Count by country:**
```sql
SELECT country, COUNT(*) as employee_count
FROM audit_users
WHERE deletion_date IS NULL
GROUP BY country
ORDER BY employee_count DESC;
```

**France vs International:**
```sql
SELECT 
    CASE WHEN country = 'France' THEN 'France' ELSE 'International' END as location_group,
    COUNT(*) as employee_count
FROM audit_users
WHERE deletion_date IS NULL
GROUP BY location_group;
```

---

## 2. Table: `paths_sessions`

**Description:** 360Learning course completions and enrollments.

**Row Count:** 62,853

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | integer | Unique record identifier |
| path_title | text | Course name |
| path_id | text | 360Learning course/path identifier |
| additional_path_information | text | Extra course details |
| user_id | text | Links to audit_users.user_id |
| user_name | text |  |
| country | text |  |
| step_1_title | text |  |
| step_1_type | text |  |
| step_1_status | text |  |
| step_2_title | text |  |
| step_2_type | text |  |
| step_2_status | text |  |
| step_3_title | text |  |
| step_3_type | text |  |
| step_3_status | text |  |
| step_4_title | text |  |
| step_4_type | text |  |
| step_4_status | text |  |
| step_5_title | text |  |
| step_5_type | text |  |
| step_5_status | text |  |
| step_6_title | text |  |
| step_6_type | text |  |
| step_6_status | text |  |
| step_7_title | text |  |
| step_7_type | text |  |
| step_7_status | text |  |
| step_8_title | text |  |
| step_8_type | text |  |
| step_8_status | text |  |
| step_9_title | text |  |
| step_9_type | text |  |
| step_9_status | text |  |
| step_10_title | text |  |
| step_10_type | text |  |
| step_10_status | text |  |
| step_11_title | text |  |
| step_11_type | text |  |
| step_11_status | text |  |
| step_12_title | text |  |
| step_12_type | text |  |
| step_12_status | text |  |
| step_13_title | text |  |
| step_13_type | text |  |
| step_13_status | text |  |
| step_14_title | text |  |
| step_14_type | text |  |
| step_14_status | text |  |
| step_15_title | text |  |
| step_15_type | text |  |
| step_15_status | text |  |
| step_16_title | text |  |
| step_16_type | text |  |
| step_16_status | text |  |
| step_17_title | text |  |
| step_17_type | text |  |
| step_17_status | text |  |
| step_18_title | text |  |
| step_18_type | text |  |
| step_18_status | text |  |
| step_19_title | text |  |
| step_19_type | text |  |
| step_19_status | text |  |
| step_20_title | text |  |
| step_20_type | text |  |
| step_20_status | text |  |
| step_21_title | text |  |
| step_21_type | text |  |
| step_21_status | text |  |
| step_22_title | text |  |
| step_22_type | text |  |
| step_22_status | text |  |
| step_23_title | text |  |
| step_23_type | text |  |
| step_23_status | text |  |
| step_24_title | text |  |
| step_24_type | text |  |
| step_24_status | text |  |
| step_25_title | text |  |
| step_25_type | text |  |
| step_25_status | text |  |
| other_data | jsonb | JSONB field with additional metadata |
| created_at | timestamp without time zone | Record creation timestamp |
| is_goodhabitz | boolean | Boolean: GoodHabitz course flag |
| is_ethics | boolean | Boolean: ethics training flag |
| is_cybersecurity | boolean | Boolean: cybersecurity training flag |
| is_onboarding | boolean | Boolean: onboarding training flag |
| is_mandatory | boolean | Boolean: required training |
| completion_date | timestamp without time zone | Date course was completed |
| completion_year | integer | Year extracted from completion_date |
| completion_month | integer | Month extracted from completion_date |
| completion_day | integer | Day extracted from completion_date |
| user_email | text |  |
| user_first_name | text |  |
| user_last_name | text |  |
| user_country | text |  |
| user_company | text |  |
| user_branch | text |  |
| user_bu | text |  |
| user_place_of_work | text |  |
| user_is_manager | text |  |
| user_manager1_name | text |  |
| user_manager2_name | text |  |
| user_rrh_name | text |  |
| user_matricule | text |  |
| user_gender | text |  |
| user_start_date | text |  |
| user_account_creation_date | text |  |
| user_groups | text |  |
| user_deletion_date | text |  |
| user_automatic_deletion_date | text |  |
| user_shell | boolean |  |

### JSONB other_data Fields

The `other_data` column contains additional information:
- `Learner status`: Enrollment status
- `Progress`: Completion percentage
- `Score`: Test/quiz scores
- `Learner enrollment date`: When user enrolled
- `Time spent`: Duration in course
- `Tags`: Course categories/tags

### Sample Data

```
user_id: 5ebbfd510f1fdc5e2b8bed97
course: Amelia - Assistant(e) de mission
completed: 2025-04-09 15:04:00
progress: 100
time_spent: 00:41:58

user_id: 637b2b62edd0abf652b19fdd
course: TH - Shell Project - TS.07 Understanding Fuels + Quiz
completed: 2024-08-30 18:34:00
progress: 100
time_spent: 01:48:55

user_id: 66fa5a85815decb332a240bd
course: Beskyt Artelias data: Din guide til sikker og korrekt datahåndtering (DA/ENG VERSION)
completed: 2025-04-30 07:10:00
progress: 100
time_spent: 00:01:31

```

### Common Queries

**Course completions by year:**
```sql
SELECT completion_year, COUNT(*) as completions
FROM paths_sessions
WHERE completion_date IS NOT NULL
GROUP BY completion_year
ORDER BY completion_year;
```

**Most popular courses:**
```sql
SELECT path_title, COUNT(*) as completions
FROM paths_sessions
WHERE completion_date IS NOT NULL
  AND completion_year = 2024
GROUP BY path_title
ORDER BY completions DESC
LIMIT 10;
```

---

## 3. Table: `goodhabitz_modules`

**Description:** GoodHabitz microlearning module completions.

**Row Count:** 12,910

**CRITICAL JOIN KEY:** `audit_users.user_id = goodhabitz_modules.username`
(Note: 'username' field contains 360Learning user_ids, not usernames)

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | integer | Unique record identifier |
| username | text | 360Learning user_id (joins to audit_users.user_id) |
| modulecode | text | GoodHabitz module code |
| coursecode | text | GoodHabitz course code |
| coursecontainer | text | Course container/category |
| languagecode | text |  |
| category | text |  |
| logdate | date | Date of activity |
| score | integer |  |
| sessiontime | integer |  |
| lessonstatus | text | Completion status (completed, incomplete, etc.) |
| statuschanged | boolean | Timestamp when status changed |
| currentresult | integer |  |
| course_title_en | text | Course title in English |
| course_title_original | text |  |
| timespent2024 | integer |  |
| fiscal_year | text |  |
| completion_year | integer | Year extracted from logdate |
| completion_month | integer | Month extracted from logdate |
| completion_day | integer | Day extracted from logdate |
| user_email | text | User email (denormalized from audit_users) |
| user_first_name | text | User first name (denormalized) |
| user_last_name | text | User last name (denormalized) |
| user_country | text | User country (denormalized) |
| user_branch | text | User branch (denormalized) |
| user_bu | text | User business unit (denormalized) |
| user_rrh_name | text | User HR rep (denormalized) |
| user_deletion_date | text | User deletion date (denormalized) |
| user_shell | boolean | Shell account flag (denormalized) |

### Sample Data

```
username (user_id): 65e170235735fd4e8f24818a
course: Business Communication Skills
date: 2024-03-08
status: completed

username (user_id): 64421899772fdffc8f94d377
course: Resilience
date: 2024-10-07
status: completed

username (user_id): 63103d296b35b3bd5abdaf4f
course: Difficult conversations
date: 2024-04-29
status: completed

```

### Common Queries

**Active employees with completions:**
```sql
SELECT 
    au.user_id,
    au.email,
    au.first_name,
    au.last_name,
    COUNT(*) as modules_completed
FROM audit_users au
INNER JOIN goodhabitz_modules gm ON au.user_id = gm.username
WHERE au.deletion_date IS NULL
  AND gm.lessonstatus = 'completed'
  AND gm.completion_year = 2024
GROUP BY au.user_id, au.email, au.first_name, au.last_name
ORDER BY modules_completed DESC;
```

**Most popular courses:**
```sql
SELECT 
    course_title_en,
    COUNT(*) as completions,
    COUNT(DISTINCT username) as unique_users
FROM goodhabitz_modules
WHERE lessonstatus = 'completed'
  AND completion_year = 2024
GROUP BY course_title_en
ORDER BY completions DESC
LIMIT 15;
```

---

## 4. SCORM Tables (GlobalExam)

**Description:** Language learning activities from GlobalExam platform.

**CRITICAL JOIN KEY:** `LOWER(audit_users.email) = LOWER(scorm_*.email)`

### 4.1 scorm_attendance_2024 / scorm_attendance_2025

**Purpose:** Self-paced language learning activities

**Row Count:** 2024: 807 | 2025: 807

#### Schema

| Column | Type | Description |
|--------|------|-------------|
| email | varchar(255) | User email (PRIMARY KEY) |
| first_name | varchar(255) | User first name |
| last_name | varchar(255) | User last name |
| groups | text | User groups |
| num_activities_carried_out | integer | Number of completed activities |
| total_activity_time_minutes | numeric(10,2) | Total time spent (minutes) |
| avg_time_per_activity_minutes | numeric(10,2) | Average time per activity |
| num_courses_missed | integer | Number of missed courses |
| num_course_hours_missed_minutes | numeric(10,2) | Time missed (minutes) |
| total_reference_time_minutes | numeric(10,2) | Expected total time |
| last_login_date | date | Last login date |

#### Sample Query

```sql
SELECT 
    au.user_id,
    au.email,
    au.country,
    au.bu,
    sa.num_activities_carried_out,
    ROUND(sa.total_activity_time_minutes / 60, 2) as hours_spent
FROM audit_users au
INNER JOIN scorm_attendance_2024 sa ON LOWER(au.email) = LOWER(sa.email)
WHERE au.deletion_date IS NULL
  AND sa.num_activities_carried_out > 0
ORDER BY sa.num_activities_carried_out DESC;
```

### 4.2 scorm_live_2024 / scorm_live_2025

**Purpose:** Virtual classroom sessions with teacher

**Row Count:** 2024: 813 | 2025: 813

**Credit System:** 2 credits = 30-minute session

#### Schema

| Column | Type | Description |
|--------|------|-------------|
| email | varchar(255) | User email (PRIMARY KEY) |
| first_name | varchar(255) | User first name |
| last_name | varchar(255) | User last name |
| groups | text | User groups |
| num_credits_consumed | integer | Credits used |
| num_credits_allocated | integer | Credits allocated |
| num_sessions_completed | integer | Sessions completed |
| num_sessions_missed_by_teacher | integer | Teacher no-shows |
| num_sessions_missed_by_student | integer | Student no-shows |
| date_of_last_class | date | Last class date |

#### Sample Query

```sql
SELECT 
    au.first_name,
    au.last_name,
    au.bu,
    sl.num_credits_allocated,
    sl.num_credits_consumed,
    sl.num_sessions_completed,
    ROUND(100.0 * sl.num_credits_consumed / NULLIF(sl.num_credits_allocated, 0), 2) as utilization_pct
FROM audit_users au
INNER JOIN scorm_live_2024 sl ON LOWER(au.email) = LOWER(sl.email)
WHERE au.deletion_date IS NULL
  AND sl.num_credits_allocated > 0
ORDER BY sl.num_credits_consumed DESC
LIMIT 20;
```

---

## 5. Key Views

### 5.1 v_goodhabitz_completed

**Description:** Filtered view of completed GoodHabitz modules only

```sql
SELECT *
FROM goodhabitz_modules
WHERE lessonstatus = 'completed';
```

### 5.2 vw_scorm_employee_summary

**Description:** Per-employee SCORM activity summary

**Row Count:** 9,837

---

## 6. Natural Language → SQL Examples

Based on actual queries from analysis sessions.

### Example 1

**Question:** How many active employees completed at least one GoodHabitz module in 2024?

**SQL:**
```sql
SELECT COUNT(DISTINCT au.user_id) as active_employees
FROM audit_users au
INNER JOIN goodhabitz_modules gm ON au.user_id = gm.username
WHERE au.deletion_date IS NULL
  AND gm.lessonstatus = 'completed'
  AND gm.completion_year = 2024;
```

### Example 2

**Question:** Show me the top 10 GoodHabitz users by time spent in 2024

**SQL:**
```sql
SELECT
    au.first_name || ' ' || au.last_name as full_name,
    au.bu,
    au.country,
    COUNT(*) as modules_completed,
    ROUND(SUM(COALESCE(sessiontime, 0)) / 60.0, 2) as total_hours
FROM audit_users au
INNER JOIN goodhabitz_modules gm ON au.user_id = gm.username
WHERE au.deletion_date IS NULL
  AND gm.lessonstatus = 'completed'
  AND gm.completion_year = 2024
GROUP BY au.user_id, au.first_name, au.last_name, au.bu, au.country
ORDER BY total_hours DESC
LIMIT 10;
```

### Example 3

**Question:** Compare France vs International for GoodHabitz usage in 2024

**SQL:**
```sql
SELECT
    CASE WHEN au.country = 'France' THEN 'France' ELSE 'International' END as location_group,
    COUNT(DISTINCT au.user_id) as active_employees,
    COUNT(*) as total_modules_completed,
    ROUND(AVG(COUNT(*)) OVER (PARTITION BY CASE WHEN au.country = 'France' THEN 'France' ELSE 'International' END), 2) as avg_modules_per_employee
FROM audit_users au
INNER JOIN goodhabitz_modules gm ON au.user_id = gm.username
WHERE au.deletion_date IS NULL
  AND gm.lessonstatus = 'completed'
  AND gm.completion_year = 2024
GROUP BY location_group
ORDER BY location_group;
```

### Example 4

**Question:** What are the most popular GoodHabitz courses in 2025?

**SQL:**
```sql
SELECT
    course_title_en,
    COUNT(*) as completions,
    COUNT(DISTINCT username) as unique_users
FROM goodhabitz_modules
WHERE lessonstatus = 'completed'
  AND completion_year = 2025
GROUP BY course_title_en
ORDER BY completions DESC
LIMIT 15;
```

### Example 5

**Question:** How many active employees used SCORM (GlobalExam) in 2025?

**SQL:**
```sql
SELECT COUNT(DISTINCT au.user_id) as active_employees
FROM audit_users au
INNER JOIN scorm_attendance_2025 sa ON LOWER(au.email) = LOWER(sa.email)
WHERE au.deletion_date IS NULL
  AND sa.num_activities_carried_out > 0;
```

### Example 6

**Question:** Show virtual classes credit utilization by business unit in 2025

**SQL:**
```sql
SELECT
    au.bu as business_unit,
    COUNT(DISTINCT au.user_id) as registered_users,
    COUNT(DISTINCT CASE WHEN sl.num_credits_consumed > 0 THEN au.user_id END) as active_users,
    SUM(sl.num_credits_allocated) as credits_allocated,
    SUM(sl.num_credits_consumed) as credits_consumed,
    SUM(sl.num_credits_allocated - sl.num_credits_consumed) as credits_unused,
    ROUND(100.0 * SUM(sl.num_credits_consumed) / NULLIF(SUM(sl.num_credits_allocated), 0), 2) as utilization_rate_pct,
    SUM(sl.num_sessions_completed) as sessions_completed
FROM audit_users au
LEFT JOIN scorm_live_2025 sl ON LOWER(au.email) = LOWER(sl.email)
WHERE au.deletion_date IS NULL
  AND sl.num_credits_allocated > 0
GROUP BY au.bu
ORDER BY utilization_rate_pct DESC;
```

### Example 7

**Question:** Find all learning activities for a specific user by email

**SQL:**
```sql
-- User info
SELECT * FROM audit_users WHERE LOWER(email) = LOWER('user@example.com');

-- 360Learning courses
SELECT path_title, completion_date
FROM paths_sessions
WHERE user_id = (SELECT user_id FROM audit_users WHERE LOWER(email) = LOWER('user@example.com'))
ORDER BY completion_date DESC;

-- GoodHabitz modules
SELECT course_title_en, logdate
FROM goodhabitz_modules
WHERE username = (SELECT user_id FROM audit_users WHERE LOWER(email) = LOWER('user@example.com'))
  AND lessonstatus = 'completed'
ORDER BY logdate DESC;

-- SCORM attendance
SELECT num_activities_carried_out, total_activity_time_minutes, last_login_date
FROM scorm_attendance_2024
WHERE LOWER(email) = LOWER('user@example.com')
UNION ALL
SELECT num_activities_carried_out, total_activity_time_minutes, last_login_date
FROM scorm_attendance_2025
WHERE LOWER(email) = LOWER('user@example.com');

-- Virtual classes
SELECT num_credits_consumed, num_credits_allocated, num_sessions_completed
FROM scorm_live_2024
WHERE LOWER(email) = LOWER('user@example.com')
UNION ALL
SELECT num_credits_consumed, num_credits_allocated, num_sessions_completed
FROM scorm_live_2025
WHERE LOWER(email) = LOWER('user@example.com');
```

### Example 8

**Question:** Show monthly GoodHabitz activity trend for 2024

**SQL:**
```sql
SELECT
    TO_CHAR(logdate, 'YYYY-MM') as month,
    COUNT(*) as completions,
    COUNT(DISTINCT username) as unique_users
FROM goodhabitz_modules
WHERE lessonstatus = 'completed'
  AND completion_year = 2024
GROUP BY month
ORDER BY month;
```

### Example 9

**Question:** Which business units have the highest 360Learning completion rates?

**SQL:**
```sql
SELECT
    au.bu,
    COUNT(DISTINCT au.user_id) as total_employees,
    COUNT(DISTINCT CASE WHEN ps.completion_date IS NOT NULL THEN au.user_id END) as employees_with_completions,
    COUNT(ps.id) as total_completions,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ps.completion_date IS NOT NULL THEN au.user_id END) / COUNT(DISTINCT au.user_id), 2) as completion_rate_pct
FROM audit_users au
LEFT JOIN paths_sessions ps ON au.user_id = ps.user_id AND ps.completion_year = 2024
WHERE au.deletion_date IS NULL
GROUP BY au.bu
ORDER BY completion_rate_pct DESC;
```

### Example 10

**Question:** What percentage of active employees used any learning platform in 2024?

**SQL:**
```sql
WITH active_emp AS (
    SELECT user_id, email FROM audit_users WHERE deletion_date IS NULL
),
goodhabitz_users AS (
    SELECT DISTINCT username as user_id FROM goodhabitz_modules
    WHERE completion_year = 2024 AND lessonstatus = 'completed'
),
scorm_users AS (
    SELECT DISTINCT ae.user_id
    FROM active_emp ae
    INNER JOIN scorm_attendance_2024 sa ON LOWER(ae.email) = LOWER(sa.email)
    WHERE sa.num_activities_carried_out > 0
),
course_users AS (
    SELECT DISTINCT user_id FROM paths_sessions WHERE completion_year = 2024 AND completion_date IS NOT NULL
),
all_learners AS (
    SELECT user_id FROM goodhabitz_users
    UNION
    SELECT user_id FROM scorm_users
    UNION
    SELECT user_id FROM course_users
)
SELECT
    (SELECT COUNT(*) FROM active_emp) as total_active_employees,
    COUNT(DISTINCT al.user_id) as employees_who_learned,
    ROUND(100.0 * COUNT(DISTINCT al.user_id) / (SELECT COUNT(*) FROM active_emp), 2) as engagement_pct
FROM all_learners al;
```

---

## 7. Key Insights for AI Query Generation

### Always Filter for Active Employees
Unless specifically asked for historical/deleted users, always include:
```sql
WHERE deletion_date IS NULL
```

### Join Pattern Cheat Sheet
```sql
-- GoodHabitz
FROM audit_users au
INNER JOIN goodhabitz_modules gm ON au.user_id = gm.username

-- SCORM/GlobalExam
FROM audit_users au
INNER JOIN scorm_attendance_2024 sa ON LOWER(au.email) = LOWER(sa.email)

-- 360Learning courses
FROM audit_users au
INNER JOIN paths_sessions ps ON au.user_id = ps.user_id
```

### Time Conversions
- GoodHabitz `sessiontime` is in minutes
- SCORM columns ending in `_minutes` are already in minutes
- To convert to hours: `time_minutes / 60`
- 360Learning `Time spent` in other_data varies in format

### Common Aggregations
- Active user count: `COUNT(DISTINCT au.user_id) WHERE deletion_date IS NULL`
- Completion count: `COUNT(*)` or `COUNT(completion_date)` depending on table
- Average per employee: Use window functions or divide aggregates

### Business Unit Codes
Common BU values: BRE, EUR, EAMO, IND, VT, MI, APAC, BMI, BP, NORD, ADS, CAN, AF

### France vs International Pattern
```sql
CASE WHEN country = 'France' THEN 'France' ELSE 'International' END
```

---

## 8. Database Statistics

- **Total Users:** 14,163
- **Active Employees:** 9,837
- **360Learning Path Records:** 62,853
- **GoodHabitz Completions:** 5,993
- **SCORM Attendance 2024:** 813
- **SCORM Attendance 2025:** 813

---

**End of Documentation**

Generated: 2025-11-06 13:43:56
