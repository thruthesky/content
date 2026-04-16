---
name: register
description: "Register on a Korea SNS subsite. Provide site name/domain, email, password, and nickname to create a new account and obtain an API key. Example: '/korea:register apple.withcenter.com user@example.com pass123 JohnDoe'. Use for registration, account creation, signup, and new account creation."
---

# /korea:register — Register

Create a new account on a Korea SNS subsite and obtain an API key.

## Command Format

```
/korea:register <site_name> <email> <password> <nickname>
```

**All four parameters are required.** If any is missing, abort the task and guide the user.

## Usage Examples

```
/korea:register apple.withcenter.com user@example.com mypass123 JohnDoe
/korea:register bangphil.com test@example.com secure456 ManilaResident
```

## Execution Procedure

### Step 1: Validate required parameters

Extract the four parameters from ARGUMENTS in order:

| Order | Parameter | Required | Description |
|-------|-----------|----------|-------------|
| 1 | **site_name** | **Required** | Subsite domain (e.g., `apple.withcenter.com`, `bangphil.com`) |
| 2 | **email** | **Required** | A valid email address |
| 3 | **password** | **Required** | At least 6 characters |
| 4 | **nickname** | **Required** | Display name (nickname) |

**If a parameter is missing, immediately abort and show this guide:**

```
Missing information for registration.
Usage: /korea:register <site_name> <email> <password> <nickname>
Example: /korea:register apple.withcenter.com user@example.com mypass123 JohnDoe

Required fields:
  - site_name: subsite domain to join (e.g., apple.withcenter.com)
  - email: a valid email address
  - password: at least 6 characters
  - nickname: display name (nickname)
```

### Step 2: Build the site URL

Build the base URL from the site name:
- `apple.withcenter.com` → `https://apple.withcenter.com/api/v1`
- `bangphil.com` → `https://bangphil.com/api/v1`

If the domain does not include a protocol, prepend `https://`.

### Step 3: Run the registration

```bash
python3 skills/korea/scripts/korea_api.py --api-key "" \
  --base-url "https://{site_name}/api/v1" \
  register --email "{EMAIL}" --password "{PASSWORD}" --display-name "{NICKNAME}"
```

### Step 4: Report the result — show the API key clearly

**On success** show the API key clearly to the user in this format:

```
Registration successful.

Site: {site_name}
Email: {email}
Nickname: {nickname}
User ID: {id}

API key: {api_key}

You can use this API key with commands such as /korea:create and /korea:update.
```

**On failure** relay the error message to the user:
- `"Email already registered."` → suggest a different email or logging in instead
- `"Password must be at least 6 characters."` → ask the user to change the password
- `"Invalid email format."` → ask the user to verify the email format
- `"Registration is not allowed on the main site."` → ask the user to provide the subsite domain correctly

## Notes

- Registration is not allowed on the main site (withcenter.com) — a subsite domain is required
- Password must be at least 6 characters
- Cannot register with an already registered email
- On registration, the user is automatically logged in and an API key is issued
- The first registrant of a subsite is automatically set as the site owner (administrator)
