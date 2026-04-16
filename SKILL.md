---
name: korea
description: "Complete content management via Korea SNS (withcenter.com) REST API. API key based authentication (Authorization: Bearer). Supports user registration/login/profile updates, post CRUD, comment CRUD, file (image) uploads, site/category lookup and management, likes/bookmarks/reactions, notifications, and search. A complete API guide for external programs, AI, and software to create, update, and delete content on Korea SNS. Use when Claude performs the following tasks: (1) Korea SNS registration/login/API key retrieval (2) User profile update/avatar upload (3) Post create/update/delete/list (4) Comment create/update/delete (5) Upload images and files and attach them to posts/comments (6) Site list/category tree lookup (7) Toggle like/bookmark/reaction (8) Notifications lookup/search (9) withcenter.com API calls (10) Automatic API documentation lookup (GET /docs). Keywords: Korea SNS, withcenter, post, posts, writing, post registration, post update, post deletion, comment, comments, registration, login, profile, avatar, file upload, image, category, site, like, bookmark, reaction, notification, search, API, api_key"
---

# Korea SNS — Complete Content Management Skill

A skill that performs all content tasks such as user management, post/comment CRUD, file upload, and site/category management through the Korea SNS (withcenter.com) REST API.

## API Basics

| Item | Value |
|------|-------|
| **Base URL** | `https://withcenter.com/api/v1` |
| **Authentication** | `Authorization: Bearer {API_KEY}` header |
| **API key format** | `{user_id}-{md5_hash}` (e.g., `4-a1b2c3d4e5f6...`) |
| **Request format** | JSON: `Content-Type: application/json`, files: `multipart/form-data` |
| **Success response** | Single: `{ "data": {...} }`, list: `{ "data": [...], "meta": {...} }` |
| **Error response** | `{ "message": "error message" }` |
| **User-Agent** | `User-Agent: KoreaSNS-CLI/1.0` is required to bypass Cloudflare WAF blocking |

Three ways to pass the API key (in priority order):
1. **Authorization header** (recommended): `Authorization: Bearer {API_KEY}`
2. **api_key cookie**: `Cookie: api_key={API_KEY}`
3. **Query parameter**: `?api_key={API_KEY}`

## Automatic API Documentation Lookup

When unsure which APIs are available, call the following endpoint to get the list of APIs:

```bash
# Fetch full API documentation
curl -s https://withcenter.com/api/v1/docs \
  -H "User-Agent: KoreaSNS-CLI/1.0"

# Filter by category (auth, user, post, comment, file, site, category, notification, search)
curl -s "https://withcenter.com/api/v1/docs?category=post" \
  -H "User-Agent: KoreaSNS-CLI/1.0"
```

**Always check API documentation before starting work to identify available endpoints.**

## Workflow

### Step 1: Obtain an API key

If the user provides an API key directly, use it.
If there is no API key but an email/password is available, log in to obtain the API key.
If there is no account, register first and automatically obtain the API key.

**Important: When working on a subsite (e.g., apple.withcenter.com), always set `--base-url` to the subsite URL.**

```bash
# Register (on subsite — registration is not allowed on the main site)
python3 skills/korea/scripts/korea_api.py --api-key "" \
  --base-url "https://apple.withcenter.com/api/v1" \
  register --email "user@example.com" --password "pass123" --display-name "NewUser"

# Login
python3 skills/korea/scripts/korea_api.py --api-key "" \
  --base-url "https://apple.withcenter.com/api/v1" \
  login --email "user@example.com" --password "pass"
```

### Step 2: Check site/category

Check the target site and category before writing a post.

```bash
# List sites
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" sites

# Fetch category tree (site ID required)
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" categories --site-id 1
```

### Step 3: Execute the content task

Include `--base-url "https://<domain>/api/v1"` in every command.
In the examples below, `{BASE}` is a subsite URL such as `https://apple.withcenter.com/api/v1`.

```bash
# Post CRUD
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" --base-url "{BASE}" create --title "Title" --content "Content" [--category-id 3]
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" --base-url "{BASE}" update --id {ID} --title "New title" --content "New content"
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" --base-url "{BASE}" delete --id {ID}
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" --base-url "{BASE}" get --id {ID}
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" --base-url "{BASE}" list [--page 1] [--per-page 10] [--category free]

# Comment CRUD
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" --base-url "{BASE}" comment-create --post-id {ID} --content "Comment"
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" --base-url "{BASE}" comment-update --comment-id {ID} --content "Updated"
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" --base-url "{BASE}" comment-delete --comment-id {ID}

# Upload a file and attach it to a post
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" --base-url "{BASE}" upload --file "/path/to/image.jpg"
# → Pass the returned upload ID through --upload-ids when creating a post/comment
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" --base-url "{BASE}" create --title "Photo post" --content "Content" --upload-ids "10,11"

# Profile update
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" --base-url "{BASE}" update-profile --display-name "New name" --bio "About me"

# Avatar upload
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" --base-url "{BASE}" upload-avatar --file "/path/to/avatar.jpg"
```

### Using curl directly (alternative)

Always include the `User-Agent` header to avoid Cloudflare WAF blocking.

```bash
# Create a post
curl -s -X POST https://withcenter.com/api/v1/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"title": "Title", "content": "Content", "category_id": 3}'

# Upload a file
curl -s -X POST https://withcenter.com/api/v1/files/upload \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -F "file=@/path/to/image.jpg"

# Attach the uploaded file to a post
curl -s -X POST https://withcenter.com/api/v1/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "User-Agent: KoreaSNS-CLI/1.0" \
  -d '{"title": "Photo post", "content": "Content", "upload_ids": [10, 11]}'
```

## Notes

1. **User-Agent required**: Cloudflare WAF blocks requests without a User-Agent. When using curl, `-H "User-Agent: KoreaSNS-CLI/1.0"` is required.
2. **API key security**: Do not expose the API key in logs, files, or output.
3. **Error handling**: If the response contains a `message` field, it is an error. Relay it to the user.
4. **Permissions**: Updates/deletions are allowed only for the author or site administrators.
5. **File upload order**: Upload the file first (POST /files/upload) to receive an ID, then link it when creating the post/comment via the `upload_ids` array.
6. **Multitenant**: When working on a subsite, set the subsite URL with the `--base-url "https://<domain>/api/v1"` option. Registration/posting is not allowed on the main site (withcenter.com).
7. **Check API docs**: When unsure how to perform a task, call `GET /docs` to see the available APIs.

## Quick reference for all API routes

```
GET    /docs                           — API documentation (JSON, filter with ?category=)

POST   /auth/register                  — Register
POST   /auth/login                     — Login
POST   /auth/logout                    — Logout

GET    /me                             — Get my info
PATCH  /me                             — Update my info
POST   /me/avatar                      — Upload avatar
POST   /me/cover                       — Upload cover image

GET    /posts                          — List posts
POST   /posts                          — Create post
GET    /posts/{id}                     — Get post details
PUT    /posts/{id}                     — Update post
DELETE /posts/{id}                     — Delete post

GET    /posts/{id}/comments            — List comments
POST   /posts/{id}/comments            — Create comment
PATCH  /comments/{id}                  — Update comment
DELETE /comments/{id}                  — Delete comment

POST   /files/upload                   — Upload file (multipart/form-data)
DELETE /files/{id}                     — Delete file

GET    /sites                          — List sites
GET    /sites/{id}/categories/tree     — Category tree

POST   /posts/{id}/like                — Toggle post like
POST   /comments/{id}/like             — Toggle comment like
POST   /posts/{id}/bookmark            — Toggle bookmark
POST   /posts/{id}/reactions           — Toggle reaction

GET    /notifications                  — List notifications
GET    /search                         — Full-text search
```

## Detailed API Documentation

- **Auth/User API** (registration, login, profile update, avatar, blocking): [references/api-auth.md](references/api-auth.md)
- **Content API** (posts, comments, likes, bookmarks, reactions): [references/api-content.md](references/api-content.md)
- **System API** (file upload, sites, categories, notifications, search, reports): [references/api-system.md](references/api-system.md)
