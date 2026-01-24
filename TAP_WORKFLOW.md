# Tap Update Workflow

This document explains how tap updates work in brew-rs and how to maintain the brew-rs/core tap.

## How Tap Updates Work

### User Perspective

When users run `brew-rs tap update`, the following happens:

1. **For each installed tap**, brew-rs performs a git pull:
   - Opens the tap's git repository (e.g., `~/.local/share/brew-rs/taps/brew-rs/core/`)
   - Fetches from the remote (GitHub)
   - Performs a fast-forward merge to update to the latest version

2. **Formula updates are immediately available**:
   - After updating, formulas reflect the new versions
   - No cache invalidation needed - formulas are read directly from tap directories

3. **Users see updated package versions**:
   ```bash
   brew-rs tap update                    # Update all taps
   brew-rs tap update brew-rs/core       # Update specific tap
   brew-rs info curl                     # Shows curl 8.18.0 (updated version)
   ```

### Automatic vs Manual Updates

- **Manual updates**: Users run `brew-rs tap update` when they want latest formulas
- **Automatic updates** (when implemented): Config option `auto_update_taps = true` will:
  - Check for updates before install operations
  - Update taps if they haven't been updated recently (e.g., 24 hours)

## Maintaining the brew-rs/core Tap

### Workflow for Updating Formulas

As a maintainer, follow these steps to update package formulas:

#### 1. Find Latest Version

Search for the latest stable release:
```bash
# For curl
curl -fsSL https://curl.se/download.html | grep -oP 'curl-\d+\.\d+\.\d+' | head -1

# For jq
curl -fsSL https://api.github.com/repos/jqlang/jq/releases/latest | jq -r '.tag_name'
```

Or visit project websites/GitHub releases pages.

#### 2. Download and Verify Checksum

```bash
cd /tmp

# Download the source tarball
curl -fsSL https://curl.se/download/curl-8.18.0.tar.gz -o curl-8.18.0.tar.gz

# Compute SHA-256 checksum
shasum -a 256 curl-8.18.0.tar.gz

# Output: e9274a5f8ab5271c0e0e6762d2fce194d5f98acc568e4ce816845b2dcc0cf88f
```

#### 3. Update Formula File

Edit `formulas/{package}.toml`:

```toml
[package]
version = "8.18.0"  # Update version

[source]
url = "https://curl.se/download/curl-8.18.0.tar.gz"  # Update URL
sha256 = "e9274a5f8ab5271c0e0e6762d2fce194d5f98acc568e4ce816845b2dcc0cf88f"  # Update checksum
```

**Important**: Always verify the SHA-256 checksum matches the official release!

#### 4. Test the Formula (Optional but Recommended)

```bash
# Clone and test locally
brew-rs tap add brew-rs/core file:///path/to/local/core
brew-rs install curl
```

#### 5. Commit and Push

```bash
git add formulas/curl.toml
git commit -m "chore: update curl to 8.18.0"
git push origin main
```

Use conventional commit prefixes:
- `chore:` - Version updates, maintenance
- `feat:` - New formulas
- `fix:` - Bug fixes in formulas or build commands
- `docs:` - Documentation updates

### Adding New Formulas

To add a new package to the tap:

1. Create `formulas/{package-name}.toml` following the template in CONTRIBUTING.md
2. Verify all fields are correct (name, version, description, URLs, checksums)
3. Test the formula locally
4. Commit with: `feat: add {package-name} formula`
5. Push to GitHub

### Release Cadence

**Recommendation**:
- **Weekly**: Check for updates to popular packages (curl, jq, etc.)
- **Monthly**: Comprehensive review of all formulas
- **As-needed**: Critical security updates pushed immediately

### Automation Opportunities

Future improvements could include:

1. **GitHub Actions workflow** to check for new releases:
   ```yaml
   # .github/workflows/update-check.yml
   - Check upstream releases
   - Create PR with updated formulas
   - Auto-compute checksums
   ```

2. **Bot-generated PRs** for version bumps

3. **Automated testing** of formula builds in CI

## How Users Receive Updates

### Timeline

1. **Maintainer updates formula** → Pushes to `brew-rs/core` on GitHub
2. **User runs `brew-rs tap update`** → Pulls latest changes from GitHub
3. **Updated formulas immediately available** → Next install uses new version

### Example Timeline

```
T+0:  Curl 8.18.0 released
T+1h: Maintainer updates formula, pushes to GitHub
T+2h: User runs `brew-rs tap update`
      → Tap updated to latest commit
T+2h: User runs `brew-rs install curl`
      → Installs curl 8.18.0 (latest)
```

### No Cache Invalidation Needed

Unlike some package managers, brew-rs reads formulas directly from the tap directory. This means:

- ✓ No stale cache issues
- ✓ Updates are immediate after git pull
- ✓ No separate "database rebuild" step

## Tap Persistence (Implementation Note)

**Current Status**: Tap information is not persisted between sessions.

**Planned**: Taps will be stored in either:
1. SQLite database (`~/.local/share/brew-rs/db/taps.db`)
2. Config file (`~/.config/brew-rs/taps.toml`)

Once implemented:
- Taps survive across brew-rs invocations
- `brew-rs tap list` shows all installed taps
- `brew-rs tap update` works with persisted tap list

## Best Practices

### For Maintainers

1. **Always verify checksums** from official sources
2. **Test formulas locally** before pushing
3. **Keep commit messages clear** using conventional commits
4. **Document breaking changes** in commit messages
5. **Respond to issues** about outdated formulas promptly

### For Users

1. **Update taps regularly**: `brew-rs tap update`
2. **Check formula before installing**: `brew-rs info <package>`
3. **Report outdated formulas** via GitHub issues
4. **Contribute updates** via pull requests

## Security Considerations

### Checksum Verification

brew-rs **always verifies** SHA-256 checksums before building:

1. Download package from URL
2. Compute SHA-256 of downloaded file
3. Compare with formula's `sha256` field
4. **Abort if mismatch** - prevents tampered packages

### Mirror Fallbacks

If primary URL fails, brew-rs tries mirrors in order:

```toml
[source]
url = "https://curl.se/download/curl-8.18.0.tar.gz"
mirrors = [
    "https://github.com/curl/curl/releases/download/curl-8_18_0/curl-8.18.0.tar.gz"
]
```

All mirrors must have **identical checksums** (verified by SHA-256).

### Tap Source Trust

Users should only add taps from **trusted sources**:

```bash
# Official tap - trusted
brew-rs tap add brew-rs/core https://github.com/brew-rs/core.git

# Third-party tap - verify before adding
brew-rs tap add username/tap https://github.com/username/tap.git
```

## Future Enhancements

### Planned Features

1. **Tap versioning**: Track tap version/commit in database
2. **Update notifications**: Notify when new package versions available
3. **Bottle support**: Pre-compiled binaries for faster installation
4. **Formula linting**: Validate formulas in CI before merge
5. **Dependency graph**: Visualize package dependencies

### Community Contributions

The tap is open for community contributions! See CONTRIBUTING.md for guidelines on:
- Adding new formulas
- Updating existing formulas
- Reporting issues
- Testing formulas

---

**Questions?** Open an issue at https://github.com/brew-rs/core/issues
