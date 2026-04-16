# Auth + User API

> Parent document: [SKILL.md](../SKILL.md)

## Core Concepts

Korea SNS uses **API key based authentication** (no PHPSESSID).
The API key is dynamically generated as an MD5 hash by combining user information (user ID, email, signup timestamp) with a server secret key.

**API key format**: `{user_id}-{md5_hash}` (e.g., `42-a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4`)

## Core Logic — How to Pass the API Key

You can pass the API key in three ways (in priority order):

```bash
# 1. Authorization header (recommended — CLI, Flutter, external apps)
Authorization: Bearer 42-a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4

# 2. api_key cookie (web browser — set automatically on login)
Cookie: api_key=42-a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4

# 3. Query parameter (direct input in the browser URL)
GET /api/v1/me?api_key=42-a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4
```

## Base URL

```
Production:  https://withcenter.com/api/v1
Development: http://localhost:8080/api/v1
```

---

## 1. Authentication API

### POST /auth/register — Register

Register a new user and automatically log in.

**Authentication**: Not required

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | O | Email address |
| `password` | string | O | Password (at least 6 characters) |
| `display_name` | string | X | Display name |
| `site_id` | int | X | Site ID (default: current site) |

**Core source code**:

```bash
curl -s -X POST https://withcenter.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"email": "new@example.com", "password": "pass123", "display_name": "NewUser"}'
```

**Success response (201)**:

```json
{
  "data": {
    "id": 1,
    "firebase_uid": "auto-generated-uid",
    "site_id": 0,
    "email": "user@example.com",
    "display_name": "NewUser",
    "username": null,
    "bio": null,
    "photo_url": null,
    "cover_url": null,
    "status": "active",
    "visibility": "public",
    "role": "user",
    "api_key": "1-a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "created_at": "2025-03-29T12:00:00Z",
    "updated_at": "2025-03-29T12:00:00Z"
  }
}
```

**Error response (422)**:

```json
{ "message": "Please enter an email address." }
{ "message": "Invalid email format." }
{ "message": "Password must be at least 6 characters." }
{ "message": "Email already registered." }
```

**Business rules**:
- The first registrant of a subsite is automatically set as the site owner
- Passwords are hashed with bcrypt
- Firebase UID is generated automatically
- The `api_key` cookie is set immediately on registration (automatic login)
- The response includes an `api_key` field — external apps should store this value for subsequent requests

---

### POST /auth/login — Login

API key cookie based login.

**Authentication**: Not required

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | O | Email |
| `password` | string | O | Password |
| `site_id` | int | X | Site ID (default: current site) |

**Core source code**:

```bash
curl -s -X POST https://withcenter.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"email": "user@example.com", "password": "mypassword"}'
```

**Success response (200)**:

```json
{
  "data": {
    "id": 4,
    "email": "user@example.com",
    "display_name": "John Doe",
    "role": "user",
    "api_key": "4-88594f37e90ca97e4a8d4045fc4e5236",
    "created_at": "2025-03-29T12:00:00Z"
  }
}
```

**Error responses**:

```json
{ "message": "Please enter your email and password." }       // 422
{ "message": "Invalid email or password." }                  // 401
{ "message": "This account has been deactivated." }          // 401
```

**Business rules**:
- If Firebase UID is missing, it is generated automatically
- Sets the `api_key` cookie (automatic login)
- The response includes an `api_key` field — external apps should store this value for subsequent requests

---

### POST /auth/logout — Logout

Deletes the `api_key` cookie.

**Authentication**: Not required

```bash
curl -s -X POST https://withcenter.com/api/v1/auth/logout \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success response (200)**: `{ "data": { "message": "Logged out." } }`

---

## 2. User API

### GET /me — Get my info

**Authentication**: Required. Used to verify API key validity.

```bash
curl -s https://withcenter.com/api/v1/me \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success response (200)**: Public user information (same structure as the register response)

---

### PATCH /me — Update my info

**Authentication**: Required

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `display_name` | string | X | Display name |
| `bio` | string | X | Biography |
| `username` | string | X | Username |

**Core source code**:

```bash
curl -s -X PATCH https://withcenter.com/api/v1/me \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"display_name": "New name", "bio": "Hello!"}'
```

**Success response (200)**: Updated public user information

**Error (422)**: `{ "message": "No data to update." }`

---

### PATCH /me/settings — Update user settings

**Authentication**: Required

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `settings` | object | O | Settings key-value object |

```bash
curl -s -X PATCH https://withcenter.com/api/v1/me/settings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"settings": {"notification_enabled": true, "theme": "dark"}}'
```

---

### PATCH /me/visibility — Update profile visibility

**Authentication**: Required

| Field | Type | Required | Allowed values |
|-------|------|----------|----------------|
| `visibility` | string | O | `public`, `private`, `friends_only` |

```bash
curl -s -X PATCH https://withcenter.com/api/v1/me/visibility \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"visibility": "private"}'
```

---

### POST /me/avatar — Upload avatar

**Authentication**: Required | **Request**: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | O | Image file |

```bash
curl -s -X POST https://withcenter.com/api/v1/me/avatar \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -F "file=@/path/to/avatar.jpg"
```

**Success response (200)**:

```json
{
  "data": {
    "photo_url": "/uploads/1/a1b2c3d4.jpg",
    "upload": {
      "id": 10,
      "url": "/uploads/1/a1b2c3d4.jpg",
      "original_name": "avatar.jpg",
      "mime_type": "image/jpeg",
      "size": 52480,
      "is_image": true
    }
  }
}
```

---

### POST /me/cover — Upload cover image

**Authentication**: Required | **Request**: `multipart/form-data`

Same approach as avatar upload. The response includes a `cover_url` field.

```bash
curl -s -X POST https://withcenter.com/api/v1/me/cover \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -F "file=@/path/to/cover.jpg"
```

---

### GET /me/bookmarks — List my bookmarks

**Authentication**: Required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `target_type` | string | X | Filter: `post` or `comment` |
| `page` | int | X | Page number |
| `per_page` | int | X | Items per page |

```bash
curl -s "https://withcenter.com/api/v1/me/bookmarks?target_type=post&page=1" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

---

### GET /me/blocked-users — List my blocked users

**Authentication**: Required

```bash
curl -s "https://withcenter.com/api/v1/me/blocked-users?page=1" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

---

## 3. User Lookup/Search

### GET /users/search — Search users

**Authentication**: Required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | O | Search query (at least 1 character) |

```bash
curl -s "https://withcenter.com/api/v1/users/search?q=John" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success response (200)**:

```json
{
  "data": [
    {
      "id": 5,
      "display_name": "John Doe",
      "photo_url": "/uploads/5/avatar.jpg",
      "email": "john@example.com"
    }
  ]
}
```

---

### GET /users/{id} — Get user profile

**Authentication**: Not required

```bash
curl -s https://withcenter.com/api/v1/users/5 \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

---

### GET /users/by-uid — Look up by Firebase UID

**Authentication**: Not required

```bash
curl -s "https://withcenter.com/api/v1/users/by-uid?uid=firebase-uid-123" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

---

## 4. Block API

### POST /users/{id}/block — Block a user

**Authentication**: Required

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reason` | string | X | Block reason |

```bash
curl -s -X POST https://withcenter.com/api/v1/users/10/block \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"reason": "Spam messages"}'
```

**Error (422)**:
- `"You cannot block yourself."`
- `"User is already blocked."`

---

### DELETE /users/{id}/block — Unblock a user

**Authentication**: Required

```bash
curl -s -X DELETE https://withcenter.com/api/v1/users/10/block \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success (200)**: `{ "data": { "message": "Block removed." } }`

---

## Response Format

| Status | Structure |
|--------|-----------|
| Success (single) | `{ "data": { ... } }` |
| Success (list) | `{ "data": [...], "meta": { "current_page", "per_page", "total", "last_page" } }` |
| Error | `{ "message": "error message" }` |

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 401 | Authentication required / invalid API key |
| 403 | Forbidden |
| 404 | Resource not found |
| 422 | Validation failure |
