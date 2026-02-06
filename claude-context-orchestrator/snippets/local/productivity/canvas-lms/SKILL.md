---
name: "Canvas LMS Assistant"
description: "Use when interacting with Harvard Canvas LMS - fetching courses, assignments, grades, submissions, modules, calendar events. Trigger with CANVAS keyword."
pattern: "\\b(CANVAS)\\b[.,;:!?]?"
---

# Canvas LMS API Assistant

## Configuration

- **Base URL**: `https://canvas.harvard.edu/api/v1`
- **Token**: `1875~QhBUrmBrKVheZxm6YCvrExYJ8HtB2PQkzGRHhGZY9fDfvze7zENCKNK6HEmM7NnJ`
- **Helper script**: `/Users/wz/Desktop/zPersonalProjects/Spring2026/canvas.sh`
- **Docs**: https://canvas.instructure.com/doc/api/index.html

## Warren's Spring 2026 Course IDs

| Course | Canvas ID | Code | Directory |
|--------|-----------|------|-----------|
| Modern Storage Systems | **166762** | COMPSCI 2640 | `CS2640/` |
| Intro to Ancient Roman World | **162077** | CLS-STDY 97B | `CLSSTDY97B/` |
| Landmarks of World Architecture | **162740** | HAA 11 | `HAA11/` |
| Holy Envy | **165559** | HSEMR-LE 76 | `HSEMR76/` |

## Helper Script

A helper script exists at `/Users/wz/Desktop/zPersonalProjects/Spring2026/canvas.sh`. Use it for common operations:

```bash
canvas.sh dashboard          # Weekly agenda: all deadlines + grades + announcements
canvas.sh deadlines          # All upcoming deadlines across 4 courses
canvas.sh deadlines 48h      # Assignments due within 48 hours
canvas.sh grades             # Current grade/score in each course
canvas.sh announcements      # Recent announcements across all courses
canvas.sh missing            # Submissions with "missing" status
canvas.sh modules <course>   # List modules for a course (cs2640|roman|haa11|hsemr76)
canvas.sh files <course>     # List all files in a course
canvas.sh download <course>  # Download all files from a course
canvas.sh submit-text <course> <assignment_id> <file.html>  # Submit text
canvas.sh submit-file <course> <assignment_id> <file.pdf>   # Submit file upload
canvas.sh assignment <course> <assignment_id>                # Get assignment details
canvas.sh syllabus <course>  # Fetch syllabus HTML
canvas.sh sync-schedule      # Update schedule.md files from Canvas deadlines
canvas.sh new-assignments    # Check for assignments added since last check
```

Course aliases: `cs2640`, `roman`, `haa11`, `hsemr76` (or use Canvas IDs directly).

## Raw API Reference

Authentication header for manual curl:
```bash
-H "Authorization: Bearer 1875~QhBUrmBrKVheZxm6YCvrExYJ8HtB2PQkzGRHhGZY9fDfvze7zENCKNK6HEmM7NnJ"
```

| Action | Method | Endpoint |
|--------|--------|----------|
| List courses | GET | `/courses?enrollment_state=active` |
| Get course | GET | `/courses/:id` |
| List assignments | GET | `/courses/:id/assignments?order_by=due_at` |
| Get assignment | GET | `/courses/:id/assignments/:aid` |
| My submission | GET | `/courses/:id/assignments/:aid/submissions/self` |
| Submit work | POST | `/courses/:id/assignments/:aid/submissions` |
| Request file upload | POST | `/courses/:id/assignments/:aid/submissions/self/files` |
| List modules | GET | `/courses/:id/modules?include[]=items` |
| Module items | GET | `/courses/:id/modules/:mid/items` |
| Calendar events | GET | `/calendar_events?type=assignment` |
| My enrollments/grades | GET | `/courses/:id/enrollments?user_id=self&include[]=total_scores` |
| Course files | GET | `/courses/:id/files` |
| Download file | GET | `/files/:fid/public_url` then follow redirect |
| Announcements | GET | `/announcements?context_codes[]=course_:id` |
| Syllabus | GET | `/courses/:id?include[]=syllabus_body` |
| Quizzes | GET | `/courses/:id/quizzes` |
| Quiz submissions | GET | `/courses/:id/quizzes/:qid/submissions` |

## Pagination

Canvas paginates all list responses. Check `Link` header for `rel="next"`. Use `per_page=100` (max). The helper script handles pagination automatically.

## File Upload Flow (3 steps)

1. **Notify** Canvas about the file:
```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -F "name=paper.pdf" -F "size=$(stat -f%z paper.pdf)" \
  "https://canvas.harvard.edu/api/v1/courses/CID/assignments/AID/submissions/self/files"
```
2. **Upload** to the returned `upload_url` with `upload_params`
3. **Submit** with the file ID:
```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -F "submission[submission_type]=online_upload" \
  -F "submission[file_ids][]=FILE_ID" \
  "https://canvas.harvard.edu/api/v1/courses/CID/assignments/AID/submissions"
```
