#!/usr/bin/env python3
"""Korea SNS API client — complete content management script.

Usage:
  # Register
  python3 korea_api.py --api-key "" register --email "user@example.com" --password "pass123" [--display-name "Name"]

  # Login to obtain an API key
  python3 korea_api.py --api-key "" login --email "user@example.com" --password "pass"

  # Get my info
  python3 korea_api.py --api-key KEY me

  # Update profile
  python3 korea_api.py --api-key KEY update-profile [--display-name "Name"] [--bio "Bio"]

  # Upload avatar
  python3 korea_api.py --api-key KEY upload-avatar --file "/path/to/avatar.jpg"

  # Upload file
  python3 korea_api.py --api-key KEY upload --file "/path/to/image.jpg"

  # Post CRUD
  python3 korea_api.py --api-key KEY create --title "Title" --content "Content" [--category-id 3] [--site-id 1] [--upload-ids "10,11"]
  python3 korea_api.py --api-key KEY update --id 1 --title "New title" --content "New content" [--upload-ids "12"]
  python3 korea_api.py --api-key KEY delete --id 1
  python3 korea_api.py --api-key KEY get    --id 1
  python3 korea_api.py --api-key KEY list   [--page 1] [--per-page 10] [--category free] [--site-id 1]

  # Comment
  python3 korea_api.py --api-key KEY comment-create --post-id 1 --content "Comment" [--parent-id 5] [--upload-ids "10"]
  python3 korea_api.py --api-key KEY comment-update --comment-id 1 --content "Updated"
  python3 korea_api.py --api-key KEY comment-delete --comment-id 1

  # Sites / categories
  python3 korea_api.py --api-key KEY sites [--page 1]
  python3 korea_api.py --api-key KEY categories --site-id 1

  # API documentation
  python3 korea_api.py --api-key "" docs [--category post]
"""

import argparse
import json
import mimetypes
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
import uuid
from typing import Optional

DEFAULT_BASE_URL = "https://withcenter.com/api/v1"
# Overridable with --base-url (subsite: https://apple.withcenter.com/api/v1)
BASE_URL = DEFAULT_BASE_URL


def api_request(method: str, path: str, api_key: str, data: Optional[dict] = None, params: Optional[dict] = None) -> dict:
    """Send an API request and return the JSON response."""
    url = f"{BASE_URL}{path}"

    if params:
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            url += "?" + urllib.parse.urlencode(filtered)

    body = json.dumps(data).encode() if data else None

    req = urllib.request.Request(url, data=body, method=method)
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("User-Agent", "KoreaSNS-CLI/1.0")
    if data:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            return json.loads(error_body)
        except json.JSONDecodeError:
            return {"message": f"HTTP {e.code}: {error_body}"}


def multipart_upload(path: str, api_key: str, file_path: str) -> dict:
    """Upload a file as multipart/form-data."""
    url = f"{BASE_URL}{path}"
    boundary = uuid.uuid4().hex

    filename = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(url, data=body, method="POST")
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("User-Agent", "KoreaSNS-CLI/1.0")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            return json.loads(error_body)
        except json.JSONDecodeError:
            return {"message": f"HTTP {e.code}: {error_body}"}


def output(result: dict):
    """Print the JSON result."""
    print(json.dumps(result, ensure_ascii=False, indent=2))


# --- Authentication ---

def cmd_register(args):
    """Register."""
    data = {"email": args.email, "password": args.password}
    if args.display_name:
        data["display_name"] = args.display_name
    result = api_request("POST", "/auth/register", "", data=data)
    output(result)
    if "data" in result and "api_key" in result.get("data", {}):
        print(f"\n# API key: {result['data']['api_key']}", file=sys.stderr)
        print("# Use it with the --api-key option in subsequent requests.", file=sys.stderr)


def cmd_login(args):
    """Log in and obtain an API key."""
    data = {"email": args.email, "password": args.password}
    result = api_request("POST", "/auth/login", "", data=data)
    output(result)
    if "data" in result and "api_key" in result.get("data", {}):
        print(f"\n# API key: {result['data']['api_key']}", file=sys.stderr)
        print("# Use it with the --api-key option in subsequent requests.", file=sys.stderr)


# --- User ---

def cmd_me(args):
    """Get my info."""
    result = api_request("GET", "/me", args.api_key)
    output(result)


def cmd_update_profile(args):
    """Update profile."""
    data = {}
    if args.display_name:
        data["display_name"] = args.display_name
    if args.bio:
        data["bio"] = args.bio
    if args.username:
        data["username"] = args.username
    if not data:
        print('{"message": "No fields to update."}')
        sys.exit(1)
    result = api_request("PATCH", "/me", args.api_key, data=data)
    output(result)


def cmd_upload_avatar(args):
    """Upload avatar."""
    result = multipart_upload("/me/avatar", args.api_key, args.file)
    output(result)


# --- File upload ---

def cmd_upload(args):
    """Upload file."""
    result = multipart_upload("/files/upload", args.api_key, args.file)
    output(result)
    if "data" in result and "id" in result.get("data", {}):
        print(f"\n# Upload ID: {result['data']['id']}", file=sys.stderr)
        print("# Use it with the --upload-ids option when creating a post/comment.", file=sys.stderr)


# --- Post ---

def cmd_create(args):
    """Create a post."""
    data = {"title": args.title, "content": args.content}
    if args.category_id:
        data["category_id"] = args.category_id
    if args.site_id:
        data["site_id"] = args.site_id
    if args.upload_ids:
        data["upload_ids"] = [int(x.strip()) for x in args.upload_ids.split(",")]
    if getattr(args, "topic_slug", None):
        data["topic_slug"] = args.topic_slug
    if getattr(args, "reservation_id", None):
        data["reservation_id"] = args.reservation_id
    result = api_request("POST", "/posts", args.api_key, data=data)
    output(result)


# --- AI Topic Reservation ---
# Pre-flight topic check/reserve so AI does not waste tokens generating duplicates.
# Flow: topic-coverage (list mine) -> topic-check (batch status) -> topic-reserve (atomic lock)
# -> create(topic_slug + reservation_id) -> reservation auto-consumed on successful post.

def cmd_topic_coverage(args):
    """List my posts that carry a topic_slug (paginated)."""
    params = {
        "category_id": args.category_id,
        "page": args.page,
        "per_page": args.per_page,
    }
    result = api_request("GET", "/me/topic-coverage", args.api_key, params=params)
    output(result)


def cmd_topic_reserve(args):
    """Atomically reserve a topic_slug for the current user."""
    data = {"topic_slug": args.topic_slug}
    if args.category_id is not None:
        data["category_id"] = args.category_id
    if args.ttl_minutes is not None:
        data["ttl_minutes"] = args.ttl_minutes
    result = api_request("POST", "/topics/reserve", args.api_key, data=data)
    output(result)


def cmd_topic_check(args):
    """Batch-check availability of candidate topic_slugs (dry run, no reservation)."""
    slugs = [s.strip() for s in args.topic_slugs.split(",") if s.strip()]
    result = api_request("POST", "/topics/check", args.api_key, data={"topic_slugs": slugs})
    output(result)


def cmd_update(args):
    """Update a post."""
    data = {}
    if args.title:
        data["title"] = args.title
    if args.content:
        data["content"] = args.content
    if args.category_id:
        data["category_id"] = args.category_id
    if args.upload_ids:
        data["upload_ids"] = [int(x.strip()) for x in args.upload_ids.split(",")]
    if not data:
        print('{"message": "No fields to update."}')
        sys.exit(1)
    result = api_request("PUT", f"/posts/{args.id}", args.api_key, data=data)
    output(result)


def cmd_delete(args):
    """Delete a post."""
    result = api_request("DELETE", f"/posts/{args.id}", args.api_key)
    output(result)


def cmd_get(args):
    """Get post details."""
    result = api_request("GET", f"/posts/{args.id}", args.api_key)
    output(result)


def cmd_list(args):
    """List posts."""
    params = {
        "page": args.page,
        "per_page": args.per_page,
        "category": args.category,
        "site_id": args.site_id,
        "order_by": args.order_by,
    }
    result = api_request("GET", "/posts", args.api_key, params=params)
    output(result)


# --- Comment ---

def cmd_comment_create(args):
    """Create a comment."""
    data = {"content": args.content}
    if args.parent_id:
        data["parent_id"] = args.parent_id
    if args.upload_ids:
        data["upload_ids"] = [int(x.strip()) for x in args.upload_ids.split(",")]
    result = api_request("POST", f"/posts/{args.post_id}/comments", args.api_key, data=data)
    output(result)


def cmd_comment_update(args):
    """Update a comment."""
    data = {"content": args.content}
    if args.upload_ids:
        data["upload_ids"] = [int(x.strip()) for x in args.upload_ids.split(",")]
    result = api_request("PATCH", f"/comments/{args.comment_id}", args.api_key, data=data)
    output(result)


def cmd_comment_delete(args):
    """Delete a comment."""
    result = api_request("DELETE", f"/comments/{args.comment_id}", args.api_key)
    output(result)


# --- Sites / Categories ---

def cmd_sites(args):
    """List sites."""
    params = {"page": args.page, "per_page": args.per_page}
    result = api_request("GET", "/sites", args.api_key, params=params)
    output(result)


def cmd_categories(args):
    """Get the category tree."""
    result = api_request("GET", f"/sites/{args.site_id}/categories/tree", args.api_key)
    output(result)


# --- API documentation ---

def cmd_docs(args):
    """Fetch API documentation."""
    params = {}
    if args.category:
        params["category"] = args.category
    result = api_request("GET", "/docs", "", params=params)
    output(result)


def main():
    parser = argparse.ArgumentParser(description="Korea SNS API client")
    parser.add_argument("--api-key", required=True, help="API key")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL,
                        help="API base URL (default: https://withcenter.com/api/v1, subsite: https://<domain>/api/v1)")
    sub = parser.add_subparsers(dest="command", required=True)

    # Register
    p = sub.add_parser("register", help="Register")
    p.add_argument("--email", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--display-name")

    # Login
    p = sub.add_parser("login", help="Log in and obtain an API key")
    p.add_argument("--email", required=True)
    p.add_argument("--password", required=True)

    # Me
    sub.add_parser("me", help="Get my info")

    # Update profile
    p = sub.add_parser("update-profile", help="Update profile")
    p.add_argument("--display-name")
    p.add_argument("--bio")
    p.add_argument("--username")

    # Upload avatar
    p = sub.add_parser("upload-avatar", help="Upload avatar")
    p.add_argument("--file", required=True, help="Path to the image file")

    # Upload file
    p = sub.add_parser("upload", help="Upload file")
    p.add_argument("--file", required=True, help="Path to the file to upload")

    # Create post
    p = sub.add_parser("create", help="Create a post")
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--category-id", type=int)
    p.add_argument("--site-id", type=int)
    p.add_argument("--upload-ids", help="Comma-separated upload IDs (e.g., 10,11)")
    p.add_argument("--topic-slug", help="AI duplicate-prevention slug (optional)")
    p.add_argument("--reservation-id", type=int, help="topic_reservations.id from topic-reserve (optional)")

    # Update post
    p = sub.add_parser("update", help="Update a post")
    p.add_argument("--id", required=True, type=int)
    p.add_argument("--title")
    p.add_argument("--content")
    p.add_argument("--category-id", type=int)
    p.add_argument("--upload-ids", help="Comma-separated upload IDs")

    # Delete post
    p = sub.add_parser("delete", help="Delete a post")
    p.add_argument("--id", required=True, type=int)

    # Get post
    p = sub.add_parser("get", help="Get post details")
    p.add_argument("--id", required=True, type=int)

    # List posts
    p = sub.add_parser("list", help="List posts")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--per-page", type=int, default=10)
    p.add_argument("--category")
    p.add_argument("--site-id", type=int)
    p.add_argument("--order-by")

    # Create comment
    p = sub.add_parser("comment-create", help="Create a comment")
    p.add_argument("--post-id", required=True, type=int)
    p.add_argument("--content", required=True)
    p.add_argument("--parent-id", type=int)
    p.add_argument("--upload-ids", help="Comma-separated upload IDs")

    # Update comment
    p = sub.add_parser("comment-update", help="Update a comment")
    p.add_argument("--comment-id", required=True, type=int)
    p.add_argument("--content", required=True)
    p.add_argument("--upload-ids", help="Comma-separated upload IDs")

    # Delete comment
    p = sub.add_parser("comment-delete", help="Delete a comment")
    p.add_argument("--comment-id", required=True, type=int)

    # List sites
    p = sub.add_parser("sites", help="List sites")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--per-page", type=int, default=10)

    # Category tree
    p = sub.add_parser("categories", help="Get the category tree")
    p.add_argument("--site-id", required=True, type=int)

    # API documentation
    p = sub.add_parser("docs", help="Fetch API documentation")
    p.add_argument("--category", help="Filter: auth, user, post, comment, file, site, category")

    # AI topic reservation — pre-flight duplicate check/reserve for AI content generation.
    p = sub.add_parser("topic-coverage", help="List my posts that carry a topic_slug (AI duplicate-prevention)")
    p.add_argument("--category-id", type=int)
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--per-page", type=int, default=50)

    p = sub.add_parser("topic-reserve", help="Atomically reserve a topic_slug before generating content")
    p.add_argument("--topic-slug", required=True)
    p.add_argument("--category-id", type=int)
    p.add_argument("--ttl-minutes", type=int)

    p = sub.add_parser("topic-check", help="Batch-check availability of candidate topic_slugs (dry run)")
    p.add_argument("--topic-slugs", required=True, help="Comma-separated slugs (e.g. slug-a,slug-b)")

    args = parser.parse_args()

    # Apply --base-url
    global BASE_URL
    BASE_URL = args.base_url

    commands = {
        "register": cmd_register,
        "login": cmd_login,
        "me": cmd_me,
        "update-profile": cmd_update_profile,
        "upload-avatar": cmd_upload_avatar,
        "upload": cmd_upload,
        "create": cmd_create,
        "update": cmd_update,
        "delete": cmd_delete,
        "get": cmd_get,
        "list": cmd_list,
        "comment-create": cmd_comment_create,
        "comment-update": cmd_comment_update,
        "comment-delete": cmd_comment_delete,
        "sites": cmd_sites,
        "categories": cmd_categories,
        "docs": cmd_docs,
        "topic-coverage": cmd_topic_coverage,
        "topic-reserve": cmd_topic_reserve,
        "topic-check": cmd_topic_check,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
