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

---

## AI Topic Reservation (Pre-flight duplicate prevention)

Three endpoints let an AI agent check/reserve a topic **before** spending tokens on web search and drafting. The system enforces **per-user uniqueness** on both `topic_slug` and `content_hash`, but only when `topic_slug` is present in the post — posts without `topic_slug` are treated as normal human posts and are never blocked for duplication.

**Recommended flow for AI:**

```
1. GET  /me/topic-coverage       → see which topic_slugs the user has already used
2. POST /topics/check            → batch-check 1~100 candidate slugs (dry run)
3. POST /topics/reserve          → atomically lock ONE slug (TTL default 30 min)
4. (AI now does web search + drafting — only after a 201 reserve)
5. POST /posts                   → submit with topic_slug + reservation_id
```

### GET /me/topic-coverage — List my posts that carry a topic_slug

Authenticated. Returns a paginated list of the caller's own posts that were created with a `topic_slug`. The AI uses this to learn what it has already covered before generating a new candidate.

**Query**
- `category_id` (optional int)
- `page` (default 1)
- `per_page` (default 50, max 200)

```bash
curl -s "https://withcenter.com/api/v1/me/topic-coverage?per_page=100" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Success (200)**
```json
{
  "data": [
    {
      "id": 5020,
      "topic_slug": "ph-cebu-diving",
      "title": "Cebu Diving Guide",
      "category_id": 1701,
      "created_at": "2026-04-16 05:49:58.575275+00"
    }
  ],
  "meta": { "current_page": 1, "per_page": 50, "total": 1, "last_page": 1 }
}
```

---

### POST /topics/reserve — Atomically reserve a topic_slug

Authenticated. Atomically locks a normalized `topic_slug` for the current user on the current site. The reservation expires after TTL minutes (default 30, range 1–120). Expired unconsumed reservations are cleaned up automatically on the next reserve attempt for the same slug.

**Body**
```json
{
  "topic_slug": "ph-cebu-diving",
  "category_id": 1701,
  "ttl_minutes": 30
}
```

**201 Created**
```json
{
  "data": {
    "id": 889,
    "site_id": 1,
    "user_id": 42,
    "category_id": 1701,
    "topic_slug": "ph-cebu-diving",
    "created_at": "2026-04-16T10:00:00+00:00",
    "expires_at": "2026-04-16T10:30:00+00:00",
    "consumed_at": null,
    "consumed_post_id": null
  }
}
```

**409 Conflict** — already posted or actively reserved
```json
{
  "message": "이미 예약했거나 게시한 주제입니다.",
  "errors": {
    "reason": "already_taken",
    "topic_slug": "ph-cebu-diving"
  }
}
```

**422** — slug format error or TTL out of range.

Slug normalization (applied server-side): lowercase → whitespace-to-dash → `[a-z0-9\-]` only → collapse repeated dashes → trim dashes → max 64 chars. So `"Kimchi Winter"`, `"kimchi-winter"`, and `"Kimchi--Winter "` all normalize to `kimchi-winter`.

---

### POST /topics/check — Batch-check availability (dry run)

Authenticated. Returns the status of 1~100 candidate slugs without reserving any. Useful for AI to narrow down candidates before a reserve call.

**Body**
```json
{ "topic_slugs": ["slug-a", "slug-b", "slug-c"] }
```

**200 OK**
```json
{
  "data": {
    "results": {
      "slug-a": "available",
      "slug-b": "taken_by_post",
      "slug-c": "reserved_active"
    }
  }
}
```

Statuses:
- `available` — not posted and no active reservation → safe to reserve
- `taken_by_post` — already posted by this user (deleted posts do not count)
- `reserved_active` — this user has an unconsumed, unexpired reservation

---

### POST /posts extended fields — topic_slug + reservation_id

The existing `POST /posts` endpoint accepts two new optional fields:

- `topic_slug` — opt into per-user duplicate prevention. If present, the server normalizes it, computes a `content_hash` (SHA-256 of NFC-normalized title+content), and rejects 409 on any conflict.
- `reservation_id` — the `id` returned by `POST /topics/reserve`. The server validates ownership (user_id + site_id + slug) and consumes the reservation upon success.

```bash
curl -s -X POST https://withcenter.com/api/v1/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{
        "title": "Cebu Diving Guide",
        "content": "...",
        "category_id": 1701,
        "topic_slug": "ph-cebu-diving",
        "reservation_id": 889
      }'
```

Response body adds three fields: `topic_slug`, `content_hash`, `reservation_id`.

**409 Conflict** is returned when:
- same user already posted this slug on this site, OR
- same user already posted content that produces the same `content_hash`, OR
- `reservation_id` does not match this user / site / slug, is expired, or was already consumed.
