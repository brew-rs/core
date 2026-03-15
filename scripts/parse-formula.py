#!/usr/bin/env python3
"""Parse a brew-rs formula TOML file and output build config as JSON.

Usage:
    python3 parse-formula.py formulas/zlib.toml
    python3 parse-formula.py formulas/curl.toml

Output: JSON object with source URL, SHA-256, build commands, build env,
        runtime deps, and build deps.
"""

import json
import sys
import tomllib
from pathlib import Path


def parse_formula(path: str) -> dict:
    """Parse a formula TOML file and return build config as a dict."""
    formula_path = Path(path)
    if not formula_path.exists():
        print(f"Error: Formula file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(formula_path, "rb") as f:
        data = tomllib.load(f)

    package = data.get("package", {})
    source = data.get("source", {})
    deps = data.get("dependencies", {})
    build = data.get("build", {})

    # Parse dependency strings — format is "name" or "name ^1.0" or "name >=1.0"
    runtime_deps = []
    for dep_str in deps.get("runtime", []):
        parts = dep_str.split(maxsplit=1)
        dep = {"name": parts[0]}
        if len(parts) > 1:
            dep["constraint"] = parts[1]
        runtime_deps.append(dep)

    build_deps = []
    for dep_str in deps.get("build", []):
        parts = dep_str.split(maxsplit=1)
        dep = {"name": parts[0]}
        if len(parts) > 1:
            dep["constraint"] = parts[1]
        build_deps.append(dep)

    result = {
        "name": package.get("name", ""),
        "version": package.get("version", ""),
        "description": package.get("description", ""),
        "source": {
            "url": source.get("url", ""),
            "sha256": source.get("sha256", ""),
            "mirrors": source.get("mirrors", []),
        },
        "build": {
            "commands": build.get("commands", []),
            "env": build.get("env", {}),
            "parallel": build.get("parallel", True),
        },
        "dependencies": {
            "runtime": runtime_deps,
            "build": build_deps,
        },
    }

    return result


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <formula.toml>", file=sys.stderr)
        sys.exit(1)

    config = parse_formula(sys.argv[1])
    print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()
