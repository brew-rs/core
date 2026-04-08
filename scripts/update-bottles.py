#!/usr/bin/env python3
"""Update a brew-rs formula TOML file with new bottle URLs and SHA-256 hashes.

Usage:
    python3 update-bottles.py formulas/zlib.toml \
        --platform macos-arm64 \
        --url https://github.com/brew-rs/core/releases/download/zlib-1.3.2/zlib-1.3.2.macos-arm64.bottle.tar.gz \
        --sha256 abc123...

    python3 update-bottles.py formulas/zlib.toml \
        --platform macos-arm64 --url <url> --sha256 <hash> \
        --platform macos-x86_64 --url <url2> --sha256 <hash2>

Multiple --platform/--url/--sha256 triplets can be provided to update
several platforms in one invocation.
"""

import argparse
import re
import sys
from pathlib import Path


BOTTLE_SECTION_PATTERN = re.compile(
    r'\[bottle\.[^\]]+\][ \t]*\n'
    r'url[ \t]*=[ \t]*"[^"]*"[ \t]*\n'
    r'sha256[ \t]*=[ \t]*"[^"]*"[ \t]*\n'
)


def update_bottle_section(
    content: str, platform: str, url: str, sha256: str
) -> str:
    """Update or insert a [bottle.<platform>] section in TOML content.

    Uses regex-based replacement to preserve comments and formatting.
    """
    section_header = f"[bottle.{platform}]"

    # Pattern to match an existing [bottle.<platform>] section
    # Captures everything from the header to the next section or EOF
    # Use [ \t]* (not \s*) for trailing whitespace to avoid eating blank lines
    pattern = re.compile(
        rf"(\[bottle\.{re.escape(platform)}\])[ \t]*\n"
        rf'url[ \t]*=[ \t]*"[^"]*"[ \t]*\n'
        rf'sha256[ \t]*=[ \t]*"[^"]*"[ \t]*\n',
        re.MULTILINE,
    )

    replacement = (
        f'{section_header}\n'
        f'url = "{url}"\n'
        f'sha256 = "{sha256}"\n'
    )

    if pattern.search(content):
        return pattern.sub(replacement, content)

    # Section doesn't exist — append before [build] or [dependencies] or at end
    # Find the first non-bottle section after [source]
    insert_before = None
    for marker in ["[dependencies]", "[build]"]:
        pos = content.find(marker)
        if pos != -1:
            insert_before = pos
            break

    # Check if other bottle sections exist — insert after the last one
    last_bottle_end = -1
    for m in BOTTLE_SECTION_PATTERN.finditer(content):
        last_bottle_end = m.end()

    if last_bottle_end > 0:
        # Insert after the last bottle section
        return content[:last_bottle_end] + "\n" + replacement + content[last_bottle_end:]
    elif insert_before is not None:
        # Insert before [dependencies] or [build]
        return content[:insert_before] + replacement + "\n" + content[insert_before:]
    else:
        # Append at end
        return content.rstrip() + "\n\n" + replacement


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update bottle URLs and SHA-256 hashes in a formula TOML file."
    )
    parser.add_argument("formula", help="Path to the formula TOML file")
    parser.add_argument(
        "--platform",
        action="append",
        required=True,
        help="Platform key (e.g., macos-arm64). Can be specified multiple times.",
    )
    parser.add_argument(
        "--url",
        action="append",
        required=True,
        help="Bottle URL. Must match the number of --platform args.",
    )
    parser.add_argument(
        "--sha256",
        action="append",
        required=True,
        help="Bottle SHA-256. Must match the number of --platform args.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the updated TOML instead of writing it.",
    )

    args = parser.parse_args()

    if len(args.platform) != len(args.url) or len(args.platform) != len(args.sha256):
        print(
            "Error: --platform, --url, and --sha256 must be specified the same number of times.",
            file=sys.stderr,
        )
        sys.exit(1)

    formula_path = Path(args.formula)
    if not formula_path.exists():
        print(f"Error: Formula file not found: {args.formula}", file=sys.stderr)
        sys.exit(1)

    content = formula_path.read_text()

    for platform, url, sha256 in zip(args.platform, args.url, args.sha256):
        # Validate SHA-256 format
        if len(sha256) != 64 or not all(c in "0123456789abcdef" for c in sha256):
            print(
                f"Error: Invalid SHA-256 for {platform}: {sha256}",
                file=sys.stderr,
            )
            sys.exit(1)

        content = update_bottle_section(content, platform, url, sha256)
        print(f"Updated {platform}: {url[:60]}...", file=sys.stderr)

    if args.dry_run:
        print(content)
    else:
        formula_path.write_text(content)
        print(f"Wrote {formula_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
