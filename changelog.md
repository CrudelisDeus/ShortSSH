# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [v0.1.0] - 2025-01-26

- Added basic functionality for working with ~/.ssh/config.
- Added automatic SSH key generation for passwordless SSH authentication.
- Added automatic generation of the ~/.ssh/config file.
- Added config file management features: backups, removal of old backups, and switching between backup versions.
- Added a manual option to copy the public key to the server without using the config file.

## [v0.1.1] - 2025-02-09
Fixed

- Fixed an issue on Windows where the menu would not open after adding a host.

## [v0.1.2] - 2025-02-10
Added

- Added support for SSH port forwarding. When adding a host, you can now choose between standard configuration or port forwarding.

Changed

- Improved UI and fixed minor visual issues.

## [v0.1.3] - 2025-02-16

Added

- Linux support.
- Changelog.

Changed

- Updated the README.

## [v0.1.4] - 2025-02-16

Added

- Added support for host notes (stored as `# Notes:` comments inside `~/.ssh/config`).
- Added display of the Notes column in the `--list` or `-l` output table.

Changed

- Updated the README.

## [v0.1.5] - 2025-02-17

### Added
- Group support for hosts via `# G: <group>` comments in `~/.ssh/config`.
- New CLI command `--list-group` / `-lg <group>` to list hosts for a specific group.
- Updated `--help` output to include the new group-list command.
- Optional prompts for Notes and Host Group when adding a host (press Enter to skip).

### Removed
- SSH forwarding CLI argument `--forward` / `-L` and the `ssh_port_forward()` command wrapper (regular `ssh` args are used instead).
- "Find host" menu entry from the interactive UI.

### Changed
- Host listing (`--list` / `-l`) output is now grouped (default group: `Ungrouped`) and prints group headers in the table.
- Moved "Delete SSH config" action into the "Backup/Restore/Delete SSH config" menu (consolidated config management).

## [v0.1.6] - 2025-02-20

### Added
- Auto-selection of SSH private key when exactly one key is found in `~/.ssh/`:
  - In **Add host** flow: the only key is automatically assigned to the new host (no selection menu).
  - In **Manual copy SSH key to host** flow: the only key is automatically chosen for `ssh-copy-id` / Windows `ssh` pipeline.

## [v0.1.7] - 2025-02-20

### Added
- New CLI command `--version` / `-v` to display the current ShortSSH version.
- New feature to sort `~/.ssh/config` by host groups (`# G: <group>`).
- New menu action **"Sort SSH config (by work group)"** inside the Backup/Restore menu.

  Sorting behavior:
  - Hosts are grouped by `# G: <group>` markers.
  - Groups are sorted alphabetically.
  - `Ungrouped` hosts are placed at the end of the file.
  - Hosts inside each group are sorted alphabetically.
  - Header and global entries (e.g., `Host *`) are preserved.

## [v0.1.8] - 2025-02-20
### Fixed

- Fixed a bug in SSH config sorting that could produce a “dangling” group marker (# G: ...) without a following Host block.

- Fixed incorrect parsing of Host blocks during sorting (block boundaries were detected wrong in some cases), which could lead to duplicated or misplaced # G: lines.

- Sorting now applies # G: <group> only to the next Host ... entry and never inserts extra empty group lines.

- Improved stability on Windows configs (paths like C:\Users\...) and mixed content so sorting doesn’t break formatting.

- Preserved the header/prelude (# ShortSSH Config and other global lines) reliably when sorting.

## [v0.1.9] - 2025-02-23

### Added
- New CLI command `--command` / `-c <host>` to print ready-to-copy connection commands for a host.
- Command output now includes:
  - Full `ssh` command (with `-i` IdentityFile when present).
  - Optional `ssh` command with all `LocalForward` rules expanded into `-L` args.
  - `rsync` upload command using the same SSH options via `-e "ssh ..."` (with progress).
  - `scp` upload command as an alternative to rsync.
- Added “short command” section in `--command` output:
  - Short `ssh` command.
  - Short `rsync` command.
  - Short `scp` command.

### Changed
- Improved SSH host config parsing:
  - `IdentityFile` now expands `~` to absolute path (`os.path.expanduser`).
  - `LocalForward` values are collected into a list and reused for command generation.
- Better user-facing messages and examples for invalid or empty host arguments.

## [v0.1.10] - 2026-02-23

### Added
- Automatic self-update system:
  - ShortSSH now checks for a newer version on startup.
  - User confirmation prompt before performing update.
- Cross-platform auto-update support:
  - Windows: downloads and executes installer via PowerShell (ExecutionPolicy Bypass).
  - Linux: automatically reinstalls ShortSSH into `/usr/local/bin/sssh`.

### Changed
- Installation path is now standardized to support automatic updates.
- Update process no longer requires manual reinstall commands.


## [v0.1.11] - 2026-02-23

### Fixed
- Fixed Windows self-update failure caused by attempting to overwrite a running `shortssh.exe`.
- Installer now downloads updates to a temporary file and safely replaces the executable after terminating the running process.
- Fixed update crashes when ShortSSH attempted to update itself from an active session.
- Improved overall reliability of the automatic update mechanism on Windows systems.

### Changed
- Improved self-update workflow to ensure safe executable replacement.
- Update process now exits ShortSSH automatically before applying updates.

## [v0.1.12] - 2026-02-23

### Fixed
- Fixed incorrect SSH config path detection on Windows when the user profile folder contains non-ASCII characters (e.g., `C:\Users\К`):
  - `~/.ssh/config` could resolve to `C:\Users\K\.ssh\config`, causing missing key/config errors.
  - ShortSSH now prefers `%USERPROFILE%` as the home directory on Windows to reliably locate `~\.ssh\...`.
- Fixed broken `IdentityFile` paths written into `~/.ssh/config` on Windows (mixed slashes, malformed `C:\Users\ ...` paths).
- Fixed SSH key lookup failures caused by absolute path mismatches between `USERNAME` and the real profile directory name.

### Changed
- `IdentityFile` is now written in a cross-platform form using `~/.ssh/<key>` instead of an absolute Windows path:
  - Avoids hardcoding `C:\Users\...`
  - Keeps configs portable between machines and user profiles
  - Lets OpenSSH resolve `~` correctly on Windows and Linux
- When reading host config on Windows, `IdentityFile` is kept as-is (no forced `expanduser`) to preserve `~` in `--command` output.

## [v0.1.13] - 2026-02-24

### Added
- Added global **interactive cancel support** during host creation:
  - Users can now type `q` at any input prompt in the **Add host** flow to immediately abort the operation.
  - Cancellation safely returns to the previous menu without creating or modifying SSH config entries.

### Changed
- Improved interactive UX in the **Add host** workflow by allowing fast exit without completing all prompts.
- Input handling logic was refactored to support clean interruption of multi-step operations.
