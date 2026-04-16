---
name: category
description: "List categories of a specific Korea SNS site. Specify the site name or domain to see which boards (categories) exist on that site. Examples: '/korea:category bangphil.com', '/korea:category bangphil'. Use when looking up category lists, board lists, or site categories."
---

# /korea:category — List Site Categories

List the categories (boards) of a specific site as a tree.

## Command Format

```
/korea:category <site name or domain>
```

**The first parameter (site name or domain) is required.** If it is missing, abort the task and guide the user.

## Usage Examples

```
/korea:category bangphil.com
/korea:category withcenter.com
/korea:category bangphil
```

## Execution Procedure

### Step 1: Validate required parameters

Extract the site name or domain from ARGUMENTS.

**If the parameter is missing, immediately abort and show this guide:**

```
Please enter a site name or domain.
Usage: /korea:category <site name or domain>
Example: /korea:category bangphil.com
```

### Step 2: Resolve the site ID

Find the site that matches the entered name/domain in the site list.

```bash
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" sites
```

If no match is found, show the available sites and abort.

### Step 3: Fetch the category tree

```bash
python3 skills/korea/scripts/korea_api.py --api-key "{KEY}" categories --site-id {SITE_ID}
```

### Step 4: Present the result nicely

Display the category tree in a hierarchical layout. Include each category's ID, name, type, and icon.

Output example:
```
Categories of bangphil.com:

  1. Free Board (ID: 1, type: forum)
     ├── Daily (ID: 5)
     └── Restaurants (ID: 6)
  2. Announcements (ID: 2, type: forum)
  3. Q&A (ID: 3, type: forum)
```
