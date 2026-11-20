#!/usr/bin/env python3
"""emdash-wp - publish posts and browse posts from EmDash via WordPress REST API.

Auth: WP_USER + WP_APP_PASSWORD env (Application Passwords), WP_SITE base URL.
Zero dependencies (stdlib only).

  WP_SITE=https://example.com WP_USER=me WP_APP_PASSWORD=xxxx emdash-wp list
  WP_SITE=...  emdash-wp publish FILE [--title T] [--status draft|publish]
"""
import base64
import json
import os
import sys
import urllib.request
import urllib.parse


def client():
    site = os.environ.get("WP_SITE", "").rstrip("/")
    user = os.environ.get("WP_USER", "")
    app_pw = os.environ.get("WP_APP_PASSWORD", "")
    if not (site and user and app_pw):
        sys.exit("set WP_SITE, WP_USER, WP_APP_PASSWORD")
    token = base64.b64encode(f"{user}:{app_pw}".encode()).decode()
    return site, {"Authorization": f"Basic {token}",
                  "Content-Type": "application/json",
                  "User-Agent": "EmDash/1.0"}


def req(method, path, data=None, params=None):
    site, headers = client()
    url = site + "/wp-json/wp/v2" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read()[:300].decode(errors='replace')}")


def cmd_list(args):
    per = "10"
    if "--per" in args:
        per = args[args.index("--per") + 1]
    posts = req("GET", "/posts", params={"per_page": per, "_fields": "id,date,title,link,status"})
    for p in posts:
        print(f"{p['id']}\t{p.get('status')}\t{p.get('date','')[:10]}\t{strip(p['title'].get('rendered',''))}\t{p.get('link','')}")


def strip(html):
    import re
    return re.sub(r"<[^>]+>", "", html)


def cmd_publish(args):
    if not args:
        sys.exit("usage: emdash-wp publish FILE [--title T] [--status draft|publish]")
    title = None
    status = "draft"
    if "--title" in args:
        title = args[args.index("--title") + 1]
    if "--status" in args:
        status = args[args.index("--status") + 1]
    text = open(args[0]).read()
    if title is None:
        title = text.splitlines()[0][:80] if text.strip() else "Untitled"
    post = req("POST", "/posts", {"title": title, "content": text, "status": status})
    print(f"{post['id']}\t{post.get('link','')}")


if __name__ == "__main__":
    import urllib.error  # noqa: E402
    if len(sys.argv) < 2 or sys.argv[1] not in ("list", "publish"):
        sys.exit("usage: emdash-wp [list [--per N] | publish FILE [--title T] [--status draft|publish]]")
    {"list": cmd_list, "publish": cmd_publish}[sys.argv[1]](sys.argv[2:])
