---
name: update
description: "Update a Korea SNS post. Specify the target and content using the post ID or natural language. Example: '/korea:update Please change the title of post 42'. Use for updating posts, editing posts, and updating entries."
---

# /korea:update — Update a Post

Analyze the user's natural-language request and update a Korea SNS post.

## Usage Examples

```
/korea:update Please change the title of post 42 to "Updated title".
/korea:update --id 42 --title "New title" --content "New content"
/korea:update Please update the content of the most recent post on bangphil.com.
```

## Execution Procedure

### Step 1: Validate required information

| Information | Required | Description |
|-------------|----------|-------------|
| **API key** | O | API key used for authentication |
| **Post ID** | O | ID of the post to update |
| **Updated content** | O | At least one of title, content, or category |

**When information is missing**: inform the user which fields are missing, request the input, and then abort.

Missing-info message example:
```
To update a post, the following information is required:
- Post ID: please provide the ID of the post to update.
- Updated content: what should be changed — title, content, or category?
```

### Step 2: Review the existing post

```bash
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" get --id {POST_ID}
```

If the post does not exist or you do not have permission, inform the user.

### Step 3: Update the post

```bash
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" update \
  --id {POST_ID} --title "New title" --content "New content"
```

### Step 4: Report the result

Tell the user the changes between before and after.

## Notes

- Only the author or a site administrator may update the post
- If no content to update is provided, confirm with the user what should be changed
