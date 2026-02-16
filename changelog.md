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
