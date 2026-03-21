#!/usr/bin/env python3
"""Check for new upstream versions of brew-rs formulas.

For each formula, checks the upstream source for newer releases.
Supports GitHub releases (via API) and generic URL patterns.

Usage:
    python3 check-updates.py formulas/           # Check all formulas
    python3 check-updates.py formulas/zlib.toml  # Check single formula

Output: JSON array of formulas with available updates.
"""

import json
import hashlib
import re
import sys
import tomllib
import urllib.request
import urllib.error
from pathlib import Path


def get_github_latest(owner: str, repo: str) -> dict | None:
    """Get latest release from GitHub API. Returns {tag, version, assets} or None."""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"  Warning: GitHub API failed for {owner}/{repo}: {e}", file=sys.stderr)
        return None

    tag = data.get("tag_name", "")
    # Strip common prefixes to get version
    version = tag
    for prefix in [f"{repo}-", "v", f"{repo}_", f"{repo}v"]:
        if version.lower().startswith(prefix.lower()):
            version = version[len(prefix):]
            break
    # Normalize underscores to dots (e.g., curl 8_18_0 → 8.18.0)
    version = version.replace("_", ".")

    assets = [
        {"name": a["name"], "url": a["browser_download_url"]}
        for a in data.get("assets", [])
    ]

    return {"tag": tag, "version": version, "assets": assets}


def extract_github_info(source_url: str) -> tuple[str, str] | None:
    """Extract (owner, repo) from a GitHub source URL."""
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/", source_url)
    if m:
        return m.group(1), m.group(2)
    return None


def find_source_url(
    name: str, version: str, old_url: str, tag: str, assets: list[dict]
) -> str | None:
    """Find the source tarball URL for a new version.

    Strategy:
    1. Check release assets for a matching tarball
    2. Construct URL by substituting version in the old URL pattern
    """
    # Check assets for source tarball
    tarball_patterns = [
        f"{name}-{version}.tar.gz",
        f"{name}-{version}.tar.xz",
        f"{name}_{version}.tar.gz",
    ]
    for asset in assets:
        for pattern in tarball_patterns:
            if asset["name"] == pattern:
                return asset["url"]

    # Construct URL from GitHub release tag
    github_info = extract_github_info(old_url)
    if github_info:
        owner, repo = github_info
        # GitHub releases/download URL pattern
        return f"https://github.com/{owner}/{repo}/releases/download/{tag}/{name}-{version}.tar.gz"

    return None


def download_and_hash(url: str) -> str | None:
    """Download a URL and return its SHA-256 hash."""
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            sha = hashlib.sha256()
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                sha.update(chunk)
            return sha.hexdigest()
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"  Warning: Failed to download {url}: {e}", file=sys.stderr)
        return None


def update_formula_file(path: Path, old_version: str, new_version: str, new_url: str, new_sha256: str) -> None:
    """Update a formula TOML file with new version, source URL, and SHA-256."""
    content = path.read_text()

    # Update version
    content = re.sub(
        r'(version\s*=\s*)"[^"]*"',
        rf'\g<1>"{new_version}"',
        content,
        count=1,
    )

    # Update source URL
    content = re.sub(
        r'(\[source\][\s\S]*?url\s*=\s*)"[^"]*"',
        rf'\g<1>"{new_url}"',
        content,
        count=1,
    )

    # Update source SHA-256
    content = re.sub(
        r'(\[source\][\s\S]*?sha256\s*=\s*)"[^"]*"',
        rf'\g<1>"{new_sha256}"',
        content,
        count=1,
    )

    # Update mirrors that contain the old version
    if old_version != new_version:
        content = content.replace(old_version, new_version)

    path.write_text(content)


def check_formula(path: Path) -> dict | None:
    """Check a single formula for updates. Returns update info or None."""
    with open(path, "rb") as f:
        data = tomllib.load(f)

    name = data["package"]["name"]
    current_version = data["package"]["version"]
    source_url = data["source"]["url"]

    print(f"Checking {name} (current: {current_version})...", file=sys.stderr)

    github_info = extract_github_info(source_url)
    if not github_info:
        # Check mirrors for GitHub URLs
        for mirror in data["source"].get("mirrors", []):
            github_info = extract_github_info(mirror)
            if github_info:
                break

    if not github_info:
        print(f"  Skipping {name}: no GitHub source URL found", file=sys.stderr)
        return None

    owner, repo = github_info
    latest = get_github_latest(owner, repo)
    if not latest:
        return None

    if latest["version"] == current_version:
        print(f"  {name} is up to date ({current_version})", file=sys.stderr)
        return None

    print(
        f"  Update available: {current_version} → {latest['version']}",
        file=sys.stderr,
    )

    # Find source tarball URL
    new_url = find_source_url(
        name, latest["version"], source_url, latest["tag"], latest["assets"]
    )
    if not new_url:
        print(f"  Warning: Could not determine source URL for {name} {latest['version']}", file=sys.stderr)
        return None

    # Download and verify
    print(f"  Downloading {new_url}...", file=sys.stderr)
    new_sha256 = download_and_hash(new_url)
    if not new_sha256:
        return None

    return {
        "name": name,
        "formula": str(path),
        "current_version": current_version,
        "new_version": latest["version"],
        "new_url": new_url,
        "new_sha256": new_sha256,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <formula.toml|formulas_dir/> [--apply]", file=sys.stderr)
        sys.exit(1)

    target = Path(sys.argv[1])
    apply_updates = "--apply" in sys.argv

    if target.is_dir():
        formula_files = sorted(target.glob("*.toml"))
    elif target.is_file():
        formula_files = [target]
    else:
        print(f"Error: {target} not found", file=sys.stderr)
        sys.exit(1)

    updates = []
    for formula_path in formula_files:
        if formula_path.name == "simple.toml":
            continue
        result = check_formula(formula_path)
        if result:
            updates.append(result)

            if apply_updates:
                print(f"  Applying update to {formula_path}...", file=sys.stderr)
                update_formula_file(
                    formula_path,
                    result["current_version"],
                    result["new_version"],
                    result["new_url"],
                    result["new_sha256"],
                )

    print(json.dumps(updates, indent=2))

    if updates:
        # Write formula names to a file for downstream workflow triggering
        names = [u["name"] for u in updates]
        print(f"\nFormulas with updates: {', '.join(names)}", file=sys.stderr)


if __name__ == "__main__":
    main()
