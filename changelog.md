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
