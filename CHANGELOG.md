# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to Semantic Versioning.

## [0.1.0] - 2026-02-10
### Added
- Event-driven autoswitch core based on EventBus
- Declarative media mapping via mapping.yml
- `cdspctl mapping` CLI (init, show, validate, test)
- Profile registry with CamillaDSP validation
- Manual and automatic switching modes
- Experimental YAML override support
- Systemd service integration

### Changed
- Replaced legacy autoswitch logic with policy → intent → execution pipeline
- Clear separation between domain logic and runtime/infrastructure
- CLI redesigned to be thin and intention-based

### Fixed
- Safe handling of invalid or missing mapping files
- Friendly permission error messages for state and config paths
- Improved test isolation via environment-based config directories
