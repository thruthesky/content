---
name: create-comment
description: "Create a comment on a Korea SNS post. Specify the target post and comment content in natural language. Example: '/korea:create-comment Leave the comment \"Great post!\" on post 42'. Use for writing comments, creating comments, and posting replies."
---

# /korea:create-comment — Create a Comment

Analyze the user's natural-language request and create a comment on a Korea SNS post.

## Usage Examples

```
/korea:create-comment Leave the comment "Great post!" on post 42.
/korea:create-comment --post-id 42 --content "Great post!"
/korea:create-comment Reply to comment 100 on post 42. Content: "I agree"
```

## Execution Procedure

### Step 1: Validate required information

| Information | Required | Description |
|-------------|----------|-------------|
| **API key** | O | API key used for authentication |
| **Post ID** | O | ID of the post to comment on |
| **Comment content** | O | Comment body |
| **Parent comment ID** | X | Parent comment ID when replying |

**When information is missing**: inform the user which fields are missing, request the input, and then abort.

Missing-info message example:
```
To create a comment, the following information is required:
- Post ID: which post should the comment be left on?
- Comment content: what should the comment say?
```

### Step 2: Create the comment

```bash
# Regular comment
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" comment-create \
  --post-id {POST_ID} --content "Comment content"

# Reply (with a parent comment ID)
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" comment-create \
  --post-id {POST_ID} --content "Reply content" --parent-id {PARENT_ID}
```

### Step 3: Report the result

On success, tell the user the created comment ID.

## Comment with Image Attachment

```bash
# 1. Upload the file
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" upload --file "/path/to/image.jpg"

# 2. Pass upload_ids when creating the comment
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" comment-create \
  --post-id {POST_ID} --content "Comment with photo" --upload-ids "10"
```

## Notes

- Replies can be nested up to 6 levels
- The post author and any parent comment authors receive notifications automatically
