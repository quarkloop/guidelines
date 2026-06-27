#!/usr/bin/env python3
"""
set_repo_metadata.py — Set GitHub repo metadata via the API.

Sets description, topics, and homepage URL for all quarkloop repos.
Requires a GitHub Personal Access Token with 'repo' scope.

Usage:
  # Set the token via env var:
  export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
  python3 set_repo_metadata.py

  # Or pass it directly:
  python3 set_repo_metadata.py --token ghp_xxxxxxxxxxxx

  # Dry run (show what would be set without making API calls):
  python3 set_repo_metadata.py --token ghp_xxxxxxxxxxxx --dry-run
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

# ─── Repo metadata ─────────────────────────────────────────────────────

REPOS = {
    "quark": {
        "description": "A universal runtime for programmable nodes — three-service architecture with Go control plane, Java/GraalJS data plane, and NATS-native communication.",
        "homepage": "https://quarkloop.com",
        "topics": [
            "quark", "runtime", "node", "nats", "graaljs",
            "go", "java", "quarkus", "wasm", "platform",
        ],
    },
    "agent": {
        "description": "A local operating environment for autonomous AI workspaces — supervisor, runtime, plugins, typed service functions, and tool execution.",
        "homepage": "https://quarkloop.com",
        "topics": [
            "quark", "agent", "ai", "autonomous-agents",
            "go", "rust", "nats", "supervisor", "runtime",
        ],
    },
    "quark-js": {
        "description": "TypeScript SDK for the Quark runtime — execute nodes by URI, chain pipelines, browse the catalog, and monitor runtime health.",
        "homepage": "https://quarkloop.com",
        "topics": [
            "quark", "sdk", "typescript", "nats",
            "node-execution", "wasm", "client-library",
        ],
    },
    "docs": {
        "description": "Unified documentation portal for the Quark platform — Fuma Docs (Next.js) aggregating markdown from product repos with Pagefind search.",
        "homepage": "https://quarkloop.com",
        "topics": [
            "quark", "docs", "documentation", "nextjs",
            "fumadocs", "pagefind",
        ],
    },
    "guidelines": {
        "description": "Unified specifications, templates, and tooling for consistent configuration across all quarkloop repositories.",
        "homepage": "https://quarkloop.com",
        "topics": [
            "quark", "guidelines", "specifications",
            "templates", "tooling", "standards",
        ],
    },
}


def update_repo(token: str, repo_name: str, metadata: dict, dry_run: bool = False) -> bool:
    """Update a single repo's metadata via the GitHub API."""
    url = f"https://api.github.com/repos/quarkloop/{repo_name}"

    # PATCH /repos/{owner}/{repo} — updates description and homepage
    patch_body = json.dumps({
        "description": metadata["description"],
        "homepage": metadata["homepage"],
    }).encode("utf-8")

    # PUT /repos/{owner}/{repo}/topics — sets topics (replaces existing)
    topics_body = json.dumps({
        "names": metadata["topics"],
    }).encode("utf-8")

    if dry_run:
        print(f"  [DRY RUN] {repo_name}:")
        print(f"    description: {metadata['description']}")
        print(f"    homepage:    {metadata['homepage']}")
        print(f"    topics:      {', '.join(metadata['topics'])}")
        return True

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Update description and homepage
    req = urllib.request.Request(url, data=patch_body, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 200:
                print(f"  ✓ {repo_name}: description + homepage set")
            else:
                print(f"  ✗ {repo_name}: unexpected status {resp.status}")
                return False
    except urllib.error.HTTPError as e:
        print(f"  ✗ {repo_name}: API error {e.code} — {e.read().decode()}")
        return False

    # Update topics
    topics_url = f"{url}/topics"
    req = urllib.request.Request(topics_url, data=topics_body, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 200:
                print(f"  ✓ {repo_name}: topics set ({len(metadata['topics'])} topics)")
            else:
                print(f"  ✗ {repo_name}: topics unexpected status {resp.status}")
                return False
    except urllib.error.HTTPError as e:
        print(f"  ✗ {repo_name}: topics API error {e.code} — {e.read().decode()}")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Set GitHub repo metadata for all quarkloop repositories.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be set without making API calls",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.token:
        print("Error: GitHub token required.")
        print("  Set GITHUB_TOKEN env var or pass --token ghp_xxx")
        print("  Create a token at: https://github.com/settings/tokens")
        print("  Required scope: repo (or public_repo for public repos only)")
        sys.exit(2)

    print(f"Setting metadata for {len(REPOS)} repositories...")
    print()

    success = 0
    failed = 0

    for repo_name, metadata in REPOS.items():
        if update_repo(args.token, repo_name, metadata, args.dry_run):
            success += 1
        else:
            failed += 1
        print()

    print(f"Done: {success} succeeded, {failed} failed")
    if args.dry_run:
        print("(dry run — no API calls made)")


if __name__ == "__main__":
    main()
