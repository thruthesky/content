---
name: delete-comment
description: "Delete a Korea SNS comment. Specify the comment ID to delete. Example: '/korea:delete-comment Please delete comment 100'. Use for deleting comments and removing comments."
---

# /korea:delete-comment — Delete a Comment

Delete a Korea SNS comment as requested by the user.

## Usage Examples

```
/korea:delete-comment Please delete comment 100.
/korea:delete-comment --comment-id 100
```

## Execution Procedure

### Step 1: Validate required information

| Information | Required | Description |
|-------------|----------|-------------|
| **API key** | O | API key used for authentication |
| **Comment ID** | O | ID of the comment to delete |

**When information is missing**: ask the user for the comment ID to delete and abort.

### Step 2: Confirm deletion

Deletion **cannot be undone**, so confirm with the user first.

### Step 3: Delete the comment

```bash
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" comment-delete \
  --comment-id {COMMENT_ID}
```

### Step 4: Report the result

Tell the user whether the deletion succeeded or failed.

## Notes

- Deletion is a soft delete and cannot be recovered
- Only the author or a site administrator may delete the comment
- **Always confirm with the user before deleting**
