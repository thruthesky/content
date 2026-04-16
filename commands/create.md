---
name: create
description: "Create a post on Korea SNS. The site name/domain and a prompt are both required. Example: '/korea:create bangphil.com Please post a daily experience from Manila BGC in the Free Board'. Use for writing posts, writing, post registration, and post creation."
---

# /korea:create — Create a Post

Analyze the user's natural-language request and create a post on Korea SNS.

## Command Format

```
/korea:create <site name or domain> <prompt>
```

**The first parameter (site name or domain) is required.** If it is missing, abort the task and guide the user.

## Usage Examples

```
/korea:create bangphil.com Please post a daily experience from Manila BGC in the Free Board.
/korea:create withcenter.com Write an "Announcement: Scheduled Maintenance" post in Announcements. Content: maintenance from 2 AM to 6 AM on April 15.
/korea:create bangphil.com Write a restaurant recommendation for Bonifacio under the Restaurants category.
```

## Execution Procedure

### Step 1: Validate required parameters

Extract the following information from ARGUMENTS:

| Information | Required | Description |
|-------------|----------|-------------|
| **Site name/domain** | **Required** | First token. Domain name or site name (e.g., `bangphil.com`, `withcenter.com`) |
| **Prompt** | **Required** | Remaining text. Instructions about category, title, and content |

**If a required parameter is missing, immediately abort and show this guide:**

If the site is missing:
```
Please enter a site name or domain.
Usage: /korea:create <site name or domain> <prompt>
Example: /korea:create bangphil.com Please post a daily story in the Free Board.
```

If the prompt is missing:
```
Please tell me what kind of post you want to create.
Usage: /korea:create <site name or domain> <prompt>
Example: /korea:create bangphil.com Please post a daily experience from Manila BGC in the Free Board.
```

### Step 2: Check the API key

Verify whether the user previously provided an API key or has logged in.
If there is no API key, ask for login credentials (email/password) and abort.

```
An API key is required. Provide your email and password so I can log in and obtain an API key.
```

### Step 3: Resolve the site ID

Find the site that matches the entered name/domain in the site list.

```bash
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" sites
```

If no match is found, show the available sites and abort.

### Step 4: Resolve the category

Extract category information from the prompt (e.g., "Free Board", "Announcements", "Restaurants").

```bash
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" categories --site-id {SITE_ID}
```

- If a category is specified → find its category ID
- If the category cannot be found → show the available categories and ask the user to choose
- If no category is specified → proceed without a category or ask the user to choose

### Step 5: Produce the title/content

Extract the title and content from the prompt, or have the AI generate an appropriate title and content based on the prompt's subject.

### Step 6: Create the post

```bash
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" create \
  --title "Title" --content "Content" --category-id {CAT_ID} --site-id {SITE_ID}
```

### Step 7: Report the result

On success, tell the user the created post ID and title.
On failure, relay the error message to the user.

## Post with Image Attachment

When the user requests an image attachment:

```bash
# 1. Upload the file
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" upload --file "/path/to/image.jpg"

# 2. Pass upload_ids when creating the post
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" create \
  --title "Title" --content "Content" --upload-ids "10,11" --site-id {SITE_ID}
```

## Notes

- **The site name/domain must always be the first parameter**
- If there is no API key, guide the user to log in first
- If the category is not found, show the available list
- If a title or content is not specified, the AI generates them from the prompt's subject
