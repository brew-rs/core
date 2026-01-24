# brew-rs/core

Official formula repository (tap) for [brew-rs](https://github.com/brew-rs/homebrew-rust).

## What is this?

This repository contains package formulas for brew-rs, the blazing-fast package manager written in Rust. Formulas are TOML files that describe how to download, build, and install packages.

## Formula Format

Formulas use a simple, declarative TOML format:

```toml
[package]
name = "example"
version = "1.0.0"
description = "An example package"
homepage = "https://example.com"
license = "MIT"

[source]
url = "https://example.com/example-1.0.0.tar.gz"
sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

[dependencies]
runtime = ["dep1", "dep2"]
build = ["cmake", "gcc"]

[build]
commands = [
    "./configure --prefix=$PREFIX",
    "make -j$NCPU",
    "make install"
]
```

See the [Formula Spec](https://github.com/brew-rs/homebrew-rust/blob/main/docs/FORMULA_SPEC.md) for complete documentation.

## Using This Tap

This tap is automatically added when you run `brew-rs init`. To manually add it:

```bash
brew-rs tap add brew-rs/core https://github.com/brew-rs/core.git
```

Update formulas from this tap:

```bash
brew-rs tap update
```

## Available Packages

- **curl 8.18.0** - Command-line tool for transferring data with URLs
- **jq 1.8.1** - Lightweight and flexible command-line JSON processor
- **simple** - Example package for testing

## Updating Formulas

Formulas are regularly updated to track the latest stable releases. When you run `brew-rs tap update`, you'll receive the newest versions.

See [TAP_WORKFLOW.md](TAP_WORKFLOW.md) for details on how tap updates work and how to contribute formula updates.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Individual formulas may have their own licenses. This repository itself is licensed under MIT.

---

**Part of the brew-rs project** | [Main Repository](https://github.com/brew-rs/homebrew-rust) | [Documentation](https://github.com/brew-rs/homebrew-rust/tree/main/docs)
