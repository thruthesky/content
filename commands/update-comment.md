---
name: update-comment
description: "Update a Korea SNS comment. Specify the comment ID and the new content. Example: '/korea:update-comment Please update comment 100'. Use for updating comments and editing comments."
---

# /korea:update-comment — Update a Comment

Update a Korea SNS comment as requested by the user.

## Usage Examples

```
/korea:update-comment Please change comment 100 to "Updated content".
/korea:update-comment --comment-id 100 --content "Updated content"
```

## Execution Procedure

### Step 1: Validate required information

| Information | Required | Description |
|-------------|----------|-------------|
| **API key** | O | API key used for authentication |
| **Comment ID** | O | ID of the comment to update |
| **Updated content** | O | The new comment body |

**When information is missing**: inform the user which fields are missing, request the input, and then abort.

### Step 2: Update the comment

```bash
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" comment-update \
  --comment-id {COMMENT_ID} --content "Updated content"
```

### Step 3: Report the result

Tell the user whether the update succeeded or failed.

## Notes

- Only the author or a site administrator may update the comment
