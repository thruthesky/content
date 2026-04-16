---
name: delete
description: "Delete a Korea SNS post. Specify the post ID to delete. Example: '/korea:delete Please delete post 42'. Use for deleting posts, removing posts, and deleting entries."
---

# /korea:delete — Delete a Post

Delete a Korea SNS post as requested by the user.

## Usage Examples

```
/korea:delete Please delete post 42.
/korea:delete --id 42
```

## Execution Procedure

### Step 1: Validate required information

| Information | Required | Description |
|-------------|----------|-------------|
| **API key** | O | API key used for authentication |
| **Post ID** | O | ID of the post to delete |

**When information is missing**: ask the user for the post ID to delete and abort.

### Step 2: Review and confirm deletion

```bash
# Check the post content before deleting
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" get --id {POST_ID}
```

Deletion **cannot be undone**, so show the user the title and content of the target post and confirm.

### Step 3: Delete the post

```bash
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" delete --id {POST_ID}
```

### Step 4: Report the result

Tell the user whether the deletion succeeded or failed.

## Notes

- Deletion is a soft delete (sets `deleted_at`) and cannot be recovered
- Only the author or a site administrator may delete the post
- **Always confirm with the user before deleting**
