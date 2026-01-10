# Parent Children's Courses API

## Endpoint

**GET** `/api/users/parent/children-courses/`

## Description

This endpoint allows parents to view all courses their children are enrolled in. The data is grouped by child, showing each child's course enrollments with progress details.

## Authentication

- **Required**: Yes
- **Permission**: Only parents can access this endpoint

## Request

```http
GET /api/users/parent/children-courses/
Authorization: Bearer <token>
```

## Response

### Success (200 OK)

```json
{
  "parent_name": "John Doe",
  "parent_email": "parent@example.com",
  "total_children": 2,
  "children": [
    {
      "child": {
        "id": 1,
        "email": "student1@example.com",
        "first_name": "Alice",
        "last_name": "Smith",
        "role": "student",
        "username": "student1@example.com",
        "date_joined": "2024-01-01T00:00:00Z",
        "is_verified": true,
        "profile": {
          "id": 1,
          "date_of_birth": "2010-05-15",
          "gender": "female",
          "phone_number": "+1234567890",
          "address": "123 Main St"
        },
        "linking_code": "ABC-123456789"
      },
      "student_id": "STU001",
      "current_class": "Grade 8",
      "current_school": "Middle School",
      "enrollments": [
        {
          "id": 1,
          "course": {
            "id": 1,
            "title": "Introduction to Python",
            "slug": "introduction-to-python",
            "price": "99.99",
            "is_published": true,
            "status": "active",
            "level": "beginner",
            "cover_image": "https://example.com/image.jpg",
            "enrollment_count": 50,
            "duration": 40,
            "start_date": "2024-01-15",
            "end_date": "2024-04-15",
            "category": 1,
            "created_at": "2024-01-01T00:00:00Z"
          },
          "student_name": "Alice Smith",
          "student_email": "student1@example.com",
          "enrolled_at": "2024-01-10T00:00:00Z",
          "completed_at": null,
          "last_accessed": "2024-01-20T10:30:00Z",
          "progress_percentage": "45.50",
          "status": "active",
          "is_active": true,
          "is_completed": false,
          "total_watch_time_minutes": 180,
          "quiz_average_score": "85.00",
          "enrollment_notes": ""
        }
      ],
      "total_enrollments": 3,
      "active_enrollments": 2,
      "completed_enrollments": 1
    }
  ],
  "total_enrollments": 5,
  "total_active_enrollments": 3,
  "total_completed_enrollments": 2
}
```

### No Children (200 OK)

```json
{
  "parent_name": "John Doe",
  "parent_email": "parent@example.com",
  "total_children": 0,
  "children": [],
  "total_enrollments": 0,
  "total_active_enrollments": 0,
  "total_completed_enrollments": 0,
  "message": "No children linked to this parent account."
}
```

### Error Responses

#### 403 Forbidden (Not a Parent)

```json
{
  "error": "Only parents can access this endpoint."
}
```

#### 404 Not Found (No Parent Profile)

```json
{
  "error": "Parent profile not found."
}
```

#### 500 Internal Server Error

```json
{
  "error": "An error occurred while retrieving children's courses."
}
```

## Response Fields

### Top Level
- `parent_name` (string): Full name of the parent
- `parent_email` (string): Email of the parent
- `total_children` (integer): Number of children linked to the parent
- `children` (array): List of children with their enrollments
- `total_enrollments` (integer): Total enrollments across all children
- `total_active_enrollments` (integer): Total active enrollments
- `total_completed_enrollments` (integer): Total completed enrollments

### Child Object
- `child` (object): User details of the child (student)
- `student_id` (string): Student ID
- `current_class` (string): Current class/grade
- `current_school` (string): Current school
- `enrollments` (array): List of course enrollments
- `total_enrollments` (integer): Total enrollments for this child
- `active_enrollments` (integer): Active enrollments for this child
- `completed_enrollments` (integer): Completed enrollments for this child

### Enrollment Object
- `id` (integer): Enrollment ID
- `course` (object): Course details
- `student_name` (string): Full name of the student
- `student_email` (string): Email of the student
- `enrolled_at` (datetime): When the student enrolled
- `completed_at` (datetime): When the course was completed (null if not completed)
- `last_accessed` (datetime): Last time the student accessed the course
- `progress_percentage` (decimal): Progress percentage (0-100)
- `status` (string): Enrollment status (active, completed, dropped, suspended)
- `is_active` (boolean): Whether enrollment is active
- `is_completed` (boolean): Whether course is completed
- `total_watch_time_minutes` (integer): Total watch time in minutes
- `quiz_average_score` (decimal): Average quiz score
- `enrollment_notes` (string): Additional notes

## Usage Examples

### cURL

```bash
curl -X GET "http://localhost:8000/api/users/parent/children-courses/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/api/users/parent/children-courses/"
headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}

response = requests.get(url, headers=headers)
data = response.json()

for child in data['children']:
    print(f"Child: {child['child']['first_name']} {child['child']['last_name']}")
    print(f"Total Enrollments: {child['total_enrollments']}")
    for enrollment in child['enrollments']:
        print(f"  - {enrollment['course']['title']}: {enrollment['progress_percentage']}%")
```

### JavaScript (fetch)

```javascript
fetch('http://localhost:8000/api/users/parent/children-courses/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log(`Total children: ${data.total_children}`);
  data.children.forEach(child => {
    console.log(`${child.child.first_name}: ${child.total_enrollments} courses`);
  });
});
```

## Notes

1. **Child Linking**: Children must be linked to the parent account using the linking code before they appear in this endpoint.

2. **Enrollment Status**: 
   - `active`: Student is currently taking the course
   - `completed`: Student has completed the course
   - `dropped`: Student dropped the course
   - `suspended`: Enrollment is suspended

3. **Progress Tracking**: Progress percentage is calculated based on completed lessons/quizzes.

4. **Performance**: The endpoint uses database optimizations (select_related, prefetch_related) for efficient queries.

5. **Caching**: Consider implementing caching for frequently accessed data if needed.

## Related Endpoints

- `POST /api/users/link-child/` - Link a child to parent account
- `GET /api/users/` - List all users
- `GET /api/courses/` - List all courses
- `GET /api/students/{id}/courses/` - Get specific student's courses

