# API Endpoints Reference

**Base URL:** `https://mobile-app-backend-ip9w.onrender.com`

## Quick Access

- **API Documentation (Swagger):** `https://mobile-app-backend-ip9w.onrender.com/api/docs/`
- **API Documentation (ReDoc):** `https://mobile-app-backend-ip9w.onrender.com/api/redoc/`
- **API Schema:** `https://mobile-app-backend-ip9w.onrender.com/api/schema/`

---

## Authentication Endpoints

**Base:** `/api/auth/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/verify-otp/` | Verify OTP code |
| POST | `/api/auth/resend-otp/` | Resend OTP code |
| POST | `/api/auth/login/` | Login user (returns JWT tokens) |
| POST | `/api/auth/forget-password/` | Request password reset OTP |
| POST | `/api/auth/reset-password/` | Reset password with OTP |
| POST | `/api/auth/check-email-exists/` | Check if email exists |
| POST | `/api/auth/delete-account/` | Delete user account |
| POST | `/api/auth/logout/` | Logout user |
| GET | `/api/auth/me/` | Get current user profile |
| POST | `/api/auth/token/refresh/` | Refresh JWT access token |

---

## User Endpoints

**Base:** `/api/users/`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/` | List all users | ✅ Yes |
| GET | `/api/users/{id}/` | Get user details | ✅ Yes |
| PUT/PATCH | `/api/users/{id}/update/` | Update user | ✅ Yes |
| POST | `/api/users/link-child/` | Link child to parent | ✅ Yes (Parent) |
| **GET** | **`/api/users/parent/children-courses/`** | **Get children's enrolled courses** | **✅ Yes (Parent)** |

### Parent Children Courses Endpoint

**Full URL:** `https://mobile-app-backend-ip9w.onrender.com/api/users/parent/children-courses/`

**Method:** `GET`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Response Example:**
```json
{
  "parent_name": "John Doe",
  "parent_email": "parent@example.com",
  "total_children": 2,
  "children": [
    {
      "child": {
        "id": 1,
        "email": "student@example.com",
        "first_name": "Alice",
        "last_name": "Smith"
      },
      "student_id": "STU001",
      "current_class": "Grade 8",
      "enrollments": [
        {
          "id": 1,
          "course": {
            "id": 1,
            "title": "Mathematics 101",
            "slug": "mathematics-101"
          },
          "progress_percentage": 75.5,
          "status": "active"
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

**cURL Example:**
```bash
curl -X GET "https://mobile-app-backend-ip9w.onrender.com/api/users/parent/children-courses/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Course Endpoints

**Base:** `/api/courses/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/courses/` | List all courses |
| POST | `/api/courses/` | Create course |
| GET | `/api/courses/{id}/` | Get course details |
| PUT | `/api/courses/{id}/` | Update course |
| DELETE | `/api/courses/{id}/` | Delete course |

### Nested Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/courses/{course_id}/lessons/` | List lessons in course |
| POST | `/api/courses/{course_id}/lessons/` | Create lesson |
| GET | `/api/courses/{course_id}/lessons/{id}/` | Get lesson details |
| GET | `/api/courses/{course_id}/enrollments/` | List enrollments |
| GET | `/api/courses/{course_id}/reviews/` | List reviews |

---

## Student Endpoints

**Base:** `/api/students/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students/` | List all students |
| GET | `/api/students/{id}/` | Get student details |
| GET | `/api/students/{id}/courses/` | Get student's courses |
| GET | `/api/students/{id}/bookmarks/` | Get student's bookmarks |

---

## WebSocket Chat Endpoint

**⚠️ Important:** WebSocket endpoints are **NOT** REST API endpoints and won't appear in Swagger/API docs.

### Chat WebSocket Connection

**URL Format:**
```
wss://mobile-app-backend-ip9w.onrender.com/ws/chat/<parent_id>/?token=<jwt_token>
```

**Example:**
```
wss://mobile-app-backend-ip9w.onrender.com/ws/chat/123/?token=eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Connection:**
```javascript
const parentId = 123; // ID of the parent you want to chat with
const token = "your_jwt_token"; // From login response
const wsUrl = `wss://mobile-app-backend-ip9w.onrender.com/ws/chat/${parentId}/?token=${token}`;
const ws = new WebSocket(wsUrl);
```

**Send Message:**
```javascript
ws.send(JSON.stringify({ message: "Hello!" }));
```

**Receive Messages:**
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Message:', data);
};
```

**Full Documentation:** See `CHAT_FRONTEND_INTEGRATION.md`

---

## Testing Endpoints

### 1. Check if API is running:
```bash
curl https://mobile-app-backend-ip9w.onrender.com/api/docs/
```

### 2. Test Parent Children Courses:
```bash
# First, login to get token
curl -X POST "https://mobile-app-backend-ip9w.onrender.com/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email": "parent@example.com", "password": "password"}'

# Then use the token
curl -X GET "https://mobile-app-backend-ip9w.onrender.com/api/users/parent/children-courses/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Test WebSocket (use a WebSocket client or browser console):
```javascript
const ws = new WebSocket('wss://mobile-app-backend-ip9w.onrender.com/ws/chat/123/?token=YOUR_TOKEN');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
```

---

## Why Chat Endpoint Doesn't Show in API Docs

**WebSocket endpoints are NOT REST API endpoints**, so they don't appear in Swagger/OpenAPI documentation. They are:

- Handled by **ASGI** (not WSGI)
- Use **WebSocket protocol** (not HTTP)
- Require **persistent connection**
- Documented separately in `CHAT_FRONTEND_INTEGRATION.md`

---

## Common Issues

### 1. "Endpoint not found"
- Check the base URL: `https://mobile-app-backend-ip9w.onrender.com`
- Ensure you're using the correct path (e.g., `/api/users/parent/children-courses/`)
- Verify the server is running (check Render logs)

### 2. "401 Unauthorized"
- Include JWT token in headers: `Authorization: Bearer <token>`
- Ensure token is not expired
- Login again to get a new token

### 3. "403 Forbidden" (Parent Children Courses)
- User must have `role: 'parent'`
- User must be authenticated
- Check user role in database

### 4. WebSocket Connection Fails
- Use `wss://` (secure) not `ws://` for HTTPS sites
- Include token in query parameter: `?token=<jwt_token>`
- Check Render logs for WebSocket errors
- Verify Daphne is running (not Gunicorn)

---

## Full API Documentation

Visit the interactive API documentation:
- **Swagger UI:** https://mobile-app-backend-ip9w.onrender.com/api/docs/
- **ReDoc:** https://mobile-app-backend-ip9w.onrender.com/api/redoc/

These will show all REST API endpoints with request/response examples.

---

**Last Updated:** January 2024

