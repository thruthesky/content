# System API (file upload, sites, categories, notifications, search, reports)

> Parent document: [SKILL.md](../SKILL.md) — see [api-auth.md](api-auth.md) for authentication

---

## 1. File Upload API

### POST /files/upload — Upload a file

**Authentication**: Required | **Request**: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | O | File to upload |

**Allowed MIME types**:
- Images: `image/jpeg`, `image/png`, `image/gif`, `image/webp`, `image/avif`
- Video: `video/mp4`
- Audio: `audio/mpeg`
- Documents: `application/pdf`, `text/plain`, `application/zip`

**File size limit**: 50 MB max

**Core source code**:

```bash
curl -s -X POST https://withcenter.com/api/v1/files/upload \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -F "file=@/path/to/image.jpg"
```

**Success response (201)**:

```json
{
  "data": {
    "id": 10,
    "url": "/uploads/1/a1b2c3d4e5f6g7h8.jpg",
    "path": "uploads/1/a1b2c3d4e5f6g7h8.jpg",
    "filename": "a1b2c3d4e5f6g7h8.jpg",
    "original_name": "image.jpg",
    "size": 102400,
    "mime_type": "image/jpeg",
    "is_image": true,
    "is_video": false
  }
}
```

**Error (422)**:
- `"No file provided."`
- `"File size exceeds 50 MB."`
- `"File type not allowed."`

**Business rules**:
- Files are stored under `/uploads/{user_id}/`
- The filename is a random 32-character hex string
- **To attach to a post/comment**, pass the returned `id` in the `upload_ids` array:
  ```json
  { "title": "Photo post", "content": "Content", "upload_ids": [10, 11] }
  ```

---

### DELETE /files/{id} — Delete a file

**Authentication**: Required (only the owner's file)

```bash
curl -s -X DELETE https://withcenter.com/api/v1/files/10 \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success (200)**: `{ "data": { "message": "File deleted." } }`

**Errors**: 403 (not the owner's file), 404 (file not found)

---

## 2. Site API

### GET /sites — List sites

**Authentication**: Not required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | int | X | Page number |
| `per_page` | int | X | Items per page (default: 10) |

```bash
curl -s "https://withcenter.com/api/v1/sites?page=1&per_page=10" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

---

### POST /sites — Create a site

**Authentication**: Not required (public site creation)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | O | Site domain |
| `name` or `site_name` | string | O | Site name |
| `owner_user_id` | int | X | Owner user ID |

```bash
curl -s -X POST https://withcenter.com/api/v1/sites \
  -H "Content-Type: application/json" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"domain": "newsite", "name": "New Site"}'
```

**Error (422)**:
- `"Please enter a domain."`
- `"Please enter a site name."`
- `"Domain already registered."`

**Business rule**: Default categories are created automatically when a site is created

---

### GET /sites/{id} — Get site details

**Authentication**: Not required

```bash
curl -s https://withcenter.com/api/v1/sites/1 \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

---

### PUT /sites/{id} — Update a site

**Authentication**: Site administrator required

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `site_name` | string | X | Site name |
| `description` | string | X | Site description |
| `settings` | object | X | Site settings |

---

## 3. Category API

### GET /sites/{id}/categories/tree — Get category tree

Returns categories in a hierarchical structure. Call before creating a post to obtain the category ID.

**Authentication**: Not required

```bash
curl -s https://withcenter.com/api/v1/sites/1/categories/tree \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success response (200)**:

```json
{
  "data": [
    {
      "id": 1,
      "name": "Free Board",
      "type": "forum",
      "parent_id": null,
      "depth": 0,
      "sort_order": 0,
      "is_visible": true,
      "icon": "fa-comments",
      "children": [
        {
          "id": 5,
          "name": "Daily",
          "parent_id": 1,
          "depth": 1,
          "children": []
        }
      ]
    }
  ]
}
```

---

### GET /sites/{id}/categories — List categories

Flat list of categories.

```bash
curl -s https://withcenter.com/api/v1/sites/1/categories \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

---

### POST /sites/{id}/categories — Create a category

**Authentication**: Site administrator required

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | O | - | Category name |
| `parent_id` | int | X | null | Parent category ID |
| `type` | string | X | `forum` | Category type |
| `icon` | string | X | `""` | Font Awesome icon class |
| `url` | string | X | `""` | URL |
| `is_visible` | bool | X | true | Visibility |

```bash
curl -s -X POST https://withcenter.com/api/v1/sites/1/categories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"name": "Restaurant Picks", "parent_id": 1, "type": "forum", "icon": "fa-utensils"}'
```

**Limits**:
- Top-level categories: up to 32
- Second-level categories: up to 64 per top-level
- Maximum depth: 3 levels

---

### PUT /categories/{id} — Update a category

**Authentication**: Site administrator required

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | X | Category name |
| `type` | string | X | Category type |
| `icon` | string | X | Icon |
| `url` | string | X | URL |
| `description` | string | X | Description |
| `is_visible` | bool | X | Visibility |

```bash
curl -s -X PUT https://withcenter.com/api/v1/categories/5 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"name": "Updated category", "icon": "fa-star"}'
```

---

### DELETE /categories/{id} — Delete a category

**Authentication**: Site administrator required

```bash
curl -s -X DELETE https://withcenter.com/api/v1/categories/5 \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Business rule**: Sub-categories are automatically promoted to the parent level

---

### PATCH /categories/{id}/move — Move a category

**Authentication**: Site administrator required

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `parent_id` | int | X | New parent category ID (null = root) |
| `sort_order` | int | X | Sort order |

**Error (422)**:
- `"You cannot set a category as its own parent."`
- `"Circular reference detected."`
- `"Maximum category depth exceeded."`

---

### POST /categories/reorder — Change category order

**Authentication**: Site administrator required

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ordered_ids` | int[] | O | Array of category IDs in the desired order |

```bash
curl -s -X POST https://withcenter.com/api/v1/categories/reorder \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"ordered_ids": [3, 1, 5, 2, 4]}'
```

**Success (200)**: `{ "data": { "message": "Order updated." } }`

---

## 4. Notification API

### GET /notifications — List notifications

**Authentication**: Required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | int | X | Page number |
| `per_page` | int | X | Items per page |

```bash
curl -s "https://withcenter.com/api/v1/notifications?page=1&per_page=20" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success response (200)**:

```json
{
  "data": [
    {
      "id": 200,
      "type": "comment_reply",
      "title": "New comment",
      "body": "John Doe left a comment.",
      "actor_user_id": 5,
      "target_type": "post",
      "target_id": 42,
      "read_at": null,
      "created_at": "2025-03-29T12:00:00Z"
    }
  ],
  "meta": { "current_page": 1, "per_page": 20, "total": 5, "last_page": 1 }
}
```

---

### GET /notifications/unread-count — Unread notification count

**Authentication**: Required

```bash
curl -s https://withcenter.com/api/v1/notifications/unread-count \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success (200)**: `{ "data": { "unread_count": 3 } }`

---

### POST /notifications/read-all — Mark all notifications as read

**Authentication**: Required

```bash
curl -s -X POST https://withcenter.com/api/v1/notifications/read-all \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success (200)**: `{ "data": { "marked_count": 3 } }`

---

### POST /notifications/{id}/read — Mark a single notification as read

**Authentication**: Required

```bash
curl -s -X POST https://withcenter.com/api/v1/notifications/200/read \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

---

## 5. Search API

### GET /search — Full-text search (MeiliSearch based)

**Authentication**: Not required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | O | Search query |
| `site_id` | int | X | Site ID |
| `category_id` | int | X | Category filter |
| `page` | int | X | Page number |
| `per_page` | int | X | Items per page (max: 100) |

```bash
curl -s "https://withcenter.com/api/v1/search?q=korea&category_id=3&page=1" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success response (200)**:

```json
{
  "data": [ ... ],
  "total": 15,
  "page": 1,
  "limit": 20,
  "query": "korea"
}
```

---

## 6. Report API

### POST /reports — Create a report

**Authentication**: Required

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target_type` | string | O | `post` or `comment` |
| `target_id` | int | O | Target ID to report |
| `report_type` | string | O | `spam`, `inappropriate`, `harassment`, `misinformation`, `copyright`, `other` |
| `reason` | string | X | Detailed reason |

```bash
curl -s -X POST https://withcenter.com/api/v1/reports \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"target_type": "post", "target_id": 42, "report_type": "spam", "reason": "Advertising spam"}'
```

**Error (422)**:
- `"Invalid report target type."`
- `"You cannot report your own content."`
- `"You have already reported this content."`

**Business rule**: A post is automatically blinded when the count of pending reports reaches 3

---

## 7. API Documentation

### GET /docs — List available APIs

Call this endpoint when you don't know which APIs exist.

**Authentication**: Not required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | X | Filter: `auth`, `user`, `post`, `comment`, `file`, `site`, `category`, `notification`, `search` |

```bash
# Full API documentation
curl -s https://withcenter.com/api/v1/docs \
  -H "User-Agent: KoreaSNS-CLI/1.0"

# Filter by category
curl -s "https://withcenter.com/api/v1/docs?category=post" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```
