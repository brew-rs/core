# Contributing to brew-rs/core

Thank you for your interest in contributing formulas to brew-rs/core!

## Adding a New Formula

1. **Create the formula file** in `formulas/{package-name}.toml`
2. **Follow the naming convention**: lowercase with hyphens (e.g., `node-js.toml`, not `NodeJS.toml`)
3. **Use the template below** as a starting point
4. **Test the formula** with `brew-rs install {package-name}`
5. **Submit a pull request**

## Formula Template

```toml
[package]
name = "package-name"
version = "1.0.0"
description = "Short description of what this package does"
homepage = "https://project-homepage.com"
license = "MIT"  # SPDX license identifier

[source]
url = "https://example.com/package-1.0.0.tar.gz"
sha256 = "ACTUAL_SHA256_CHECKSUM_HERE"
mirrors = [
    "https://mirror1.com/package-1.0.0.tar.gz",
]

[dependencies]
runtime = ["dep1", "dep2"]
build = ["cmake", "gcc"]
test = ["pytest"]

[build]
commands = [
    "./configure --prefix=$PREFIX",
    "make -j$NCPU",
    "make install"
]

[build.env]
CC = "gcc"
CFLAGS = "-O2"
```

## Validation Checklist

Before submitting:

- [ ] Package name is lowercase with hyphens only
- [ ] Version follows semantic versioning (x.y.z)
- [ ] Description is clear and concise
- [ ] URL points to official source release
- [ ] **SHA-256 checksum is correct** (verify with `shasum -a 256`)
- [ ] All dependencies are listed
- [ ] Build commands are tested and work
- [ ] Formula passes validation

## Getting SHA-256 Checksums

```bash
shasum -a 256 package-1.0.0.tar.gz
```

## Best Practices

- Use official project names (lowercase)
- Pin to specific versions
- Include mirrors for reliability
- Keep build commands simple and portable

## Questions?

Open an issue: https://github.com/brew-rs/core/issues

Thank you for contributing! 🦀
