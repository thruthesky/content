# Content API (posts, comments, likes, bookmarks, reactions)

> Parent document: [SKILL.md](../SKILL.md) — see [api-auth.md](api-auth.md) for authentication

## Core Concepts

The Korea SNS content API. It provides create/read/update/delete for posts and comments, plus likes, bookmarks, and reactions.
All write operations require authentication via the `Authorization: Bearer {API_KEY}` header.

## Core Logic

- Posts: `title` and `content` are required. `category_id` can be specified to set a category.
- Update/Delete: Only the author or a site administrator can perform them.
- Delete: Soft delete (sets `deleted_at`, not recoverable).
- Comments: Up to 6 levels of nested replies. The post author and ancestor comment authors are notified automatically.
- File attachments: Upload the file first (POST /files/upload), then pass the returned `id` in the `upload_ids` array.

## Base URL

```
https://withcenter.com/api/v1
```

---

## 1. Post API

### POST /posts — Create a post

**Authentication**: Required

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | O | Title |
| `content` | string | O | Content |
| `category_id` | int | X | Category ID |
| `site_id` | int | X | Site ID (default: current site) |
| `urls` | array | X | Array of attached URLs |
| `upload_ids` | array | X | Array of upload IDs (returned from file upload) |

**Core source code**:

```bash
curl -s -X POST https://withcenter.com/api/v1/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"title": "New post", "content": "This is the content.", "category_id": 3}'
```

**Create a post with a file attachment** (2 steps):

```bash
# Step 1: Upload the file
curl -s -X POST https://withcenter.com/api/v1/files/upload \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -F "file=@/path/to/image.jpg"
# → Response: { "data": { "id": 10, ... } }

# Step 2: Create the post with the upload ID
curl -s -X POST https://withcenter.com/api/v1/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"title": "Photo post", "content": "Content", "upload_ids": [10]}'
```

**Success response (201)**:

```json
{
  "data": {
    "id": 42,
    "uuid": "d76f60f1-2586-4229-82cc-bf4c98b12cdb",
    "site_id": 0,
    "category_id": 3,
    "user_id": 4,
    "type": "default",
    "title": "New post",
    "content": "This is the content.",
    "visibility": "public",
    "status": "published",
    "is_pinned": false,
    "published_at": null,
    "likes_count": 0,
    "comments_count": 0,
    "views_count": 0,
    "created_at": "2026-03-29T12:01:08+00",
    "updated_at": "2026-03-29T12:01:08+00",
    "deleted_at": null,
    "urls": null,
    "is_blind": false
  }
}
```

**Error (422)**:
- `"Please enter a title."`
- `"The category does not exist."`

---

### GET /posts — List posts

**Authentication**: Not required (blocked users are filtered when logged in)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `site_id` | int | X | Site ID |
| `category` | string | X | Category slug or ID |
| `page` | int | X | Page (default: 1) |
| `per_page` | int | X | Items per page (default: 20, max: 100) |
| `order_by` | string | X | Sort: `created_at`, `view_count`, `comment_count`, `like_count` |
| `order` | string | X | Direction: `asc`, `desc` (default: desc) |

```bash
curl -s "https://withcenter.com/api/v1/posts?category=free&page=1&per_page=10" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success response (200)**:

```json
{
  "data": [
    {
      "id": 42,
      "site_id": 1,
      "category_id": 3,
      "user_id": 5,
      "title": "Hello",
      "content": "This is the first post.",
      "urls": [],
      "is_pinned": false,
      "is_blind": false,
      "view_count": 15,
      "like_count": 3,
      "comment_count": 2,
      "created_at": "2025-03-29T10:00:00Z",
      "user": {
        "id": 5,
        "display_name": "John Doe",
        "photo_url": "/uploads/5/avatar.jpg"
      },
      "category": {
        "id": 3,
        "name": "Free Board"
      }
    }
  ],
  "meta": { "current_page": 1, "per_page": 10, "total": 42, "last_page": 5 }
}
```

---

### GET /posts/{id} — Get post details

**Authentication**: Not required

```bash
curl -s https://withcenter.com/api/v1/posts/42 \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

`views_count` is automatically incremented by 1 on lookup. The response includes `files`, `user`, and `category` fields.

**Success response (200)**:

```json
{
  "data": {
    "id": 42,
    "title": "Hello",
    "content": "This is the first post.",
    "view_count": 16,
    "user": { "id": 5, "display_name": "John Doe", "photo_url": "..." },
    "category": { "id": 3, "name": "Free Board" },
    "files": [
      {
        "id": 10,
        "url": "/uploads/5/image1.jpg",
        "original_name": "photo.jpg",
        "mime_type": "image/jpeg",
        "size": 102400,
        "is_image": true,
        "width": 1920,
        "height": 1080
      }
    ]
  }
}
```

---

### PUT /posts/{id} — Update a post

**Authentication**: Required (author or site administrator)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | X | Title |
| `content` | string | X | Content |
| `category_id` | int | X | Category ID |
| `urls` | array | X | Array of attached URLs |
| `upload_ids` | array | X | Array of new upload IDs to attach |

```bash
curl -s -X PUT https://withcenter.com/api/v1/posts/42 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"title": "Updated title", "content": "Updated content"}'
```

**Errors**: 403 (`"You do not have permission to update."`), 404 (`"Post not found."`)

---

### DELETE /posts/{id} — Delete a post

**Authentication**: Required (author or site administrator)

```bash
curl -s -X DELETE https://withcenter.com/api/v1/posts/42 \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success (200)**: `{ "data": { "message": "Post deleted." } }`

**Business rule**: Soft delete (sets `deleted_at`)

---

### POST /posts/{id}/pin — Pin a post

**Authentication**: Site administrator required

```bash
curl -s -X POST https://withcenter.com/api/v1/posts/42/pin \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

### DELETE /posts/{id}/pin — Unpin a post

**Authentication**: Site administrator required

```bash
curl -s -X DELETE https://withcenter.com/api/v1/posts/42/pin \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

---

## 2. Comment API

### POST /posts/{id}/comments — Create a comment

**Authentication**: Required

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string | O | Comment content |
| `parent_id` | int | X | Parent comment ID (reply, up to 6 levels) |
| `urls` | array | X | Array of attached URLs |
| `upload_ids` | array | X | Array of upload IDs |

```bash
curl -s -X POST https://withcenter.com/api/v1/posts/42/comments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"content": "Great post!"}'
```

**Create a reply**:

```bash
curl -s -X POST https://withcenter.com/api/v1/posts/42/comments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"content": "This is a reply.", "parent_id": 100}'
```

**Error (422)**:
- `"Please enter the comment content."`
- `"Post not found."`
- `"Parent comment not found."`
- `"Maximum reply depth exceeded."`

**Business rules**:
- Maximum reply depth: 6 levels
- The post author is notified automatically
- Parent/ancestor comment authors are notified automatically (up to 10 levels)

---

### GET /posts/{id}/comments — List comments

**Authentication**: Not required (blocked users are filtered when logged in)

```bash
curl -s https://withcenter.com/api/v1/posts/42/comments \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success response (200)**:

```json
{
  "data": {
    "data": [
      {
        "id": 100,
        "post_id": 42,
        "user_id": 5,
        "parent_id": null,
        "content": "Great post!",
        "urls": [],
        "like_count": 2,
        "created_at": "2025-03-29T11:00:00Z",
        "user": {
          "id": 5,
          "display_name": "John Doe",
          "photo_url": "/uploads/5/avatar.jpg"
        },
        "files": []
      }
    ],
    "total": 5
  }
}
```

---

### PATCH /comments/{id} — Update a comment

**Authentication**: Required (author or administrator)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string | O | Updated content |
| `urls` | array | X | Array of attached URLs |
| `upload_ids` | array | X | Array of new upload IDs to attach |

```bash
curl -s -X PATCH https://withcenter.com/api/v1/comments/100 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"content": "Updated comment"}'
```

---

### DELETE /comments/{id} — Delete a comment

**Authentication**: Required (author or administrator)

```bash
curl -s -X DELETE https://withcenter.com/api/v1/comments/100 \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success (200)**: `{ "data": { "message": "Comment deleted." } }`

---

## 3. Like API

### POST /posts/{id}/like — Toggle post like

Adds a like if none exists, removes it otherwise (toggle).

**Authentication**: Required

```bash
curl -s -X POST https://withcenter.com/api/v1/posts/42/like \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success response (200)**:

```json
{ "data": { "action": "liked", "like_count": 4 } }
// or
{ "data": { "action": "unliked", "like_count": 3 } }
```

**Business rule**: When a like is added, the post author is notified (excluding the author's own posts)

---

### POST /comments/{id}/like — Toggle comment like

**Authentication**: Required

```bash
curl -s -X POST https://withcenter.com/api/v1/comments/100/like \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

---

## 4. Bookmark API

### POST /posts/{id}/bookmark — Toggle bookmark

**Authentication**: Required

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `target_type` | string | X | `post` | `post` or `comment` |

```bash
curl -s -X POST https://withcenter.com/api/v1/posts/42/bookmark \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"target_type": "post"}'
```

**Success (200)**: `{ "data": { "action": "bookmarked", "target_type": "post", "target_id": 42 } }`

---

### DELETE /posts/{id}/bookmark — Remove bookmark

**Authentication**: Required

```bash
curl -s -X DELETE https://withcenter.com/api/v1/posts/42/bookmark \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success (200)**: `{ "data": { "message": "Bookmark removed." } }`

---

## 5. Reaction API

### POST /posts/{id}/reactions — Toggle post reaction

**Authentication**: Required

| Field | Type | Required | Default | Allowed values |
|-------|------|----------|---------|----------------|
| `reaction_type` | string | X | `like` | `like`, `love`, `haha`, `wow`, `sad`, `angry` |

```bash
curl -s -X POST https://withcenter.com/api/v1/posts/42/reactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"reaction_type": "love"}'
```

**Success (200)**:

```json
{ "data": { "action": "reacted", "target_type": "post", "target_id": 42 } }
// or (already reacted)
{ "data": { "action": "unreacted", "target_type": "post", "target_id": 42 } }
```

---

### POST /comments/{id}/reactions — Toggle comment reaction

Same approach as post reactions. `target_type` is automatically set to `comment`.

```bash
curl -s -X POST https://withcenter.com/api/v1/comments/100/reactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"reaction_type": "haha"}'
```
