# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-08-25

### Added
- Real-time Live interface for CLI with dynamic table updates
- Modern progress bar with visual feedback
- Full-width responsive layout for all components
- Comprehensive professional README with screenshots
- Improved IP geolocation with multiple backup APIs

### Changed
- CLI now displays all content in a single Live interface
- Progress bar and table updates in real-time with sorting
- Optimized performance with reduced refresh rates
- Enhanced banner and network info panels
- Improved error handling for network information retrieval

### Fixed
- CLI interface performance optimizations
- Removed unnecessary spacing in progress display
- Stabilized IP information display (no more flickering)
- Layout alignment issues with Chinese characters in tables

## [2.0.0] - 2024-01-14

### Added
- Complete code refactoring with modular architecture
- CLI version with rich terminal interface
- Docker support for easy deployment
- GitHub templates for issues and PRs
- Contributing guidelines and Code of Conduct
- Export functionality (JSON, CSV, Markdown)
- Region recommendation based on use case
- Proper logging system
- Type hints for better code quality

### Changed
- Restructured code into separate modules (src/)
- Improved error handling and resilience
- Enhanced UI with better visual feedback
- Optimized concurrent testing performance

### Fixed
- macOS/Linux ping parsing issues
- Progress bar update problems
- Thread execution in debug mode

## [1.0.0] - 2024-01-10

### Added
- Initial release
- Web interface for network testing
- Support for 24 Oracle Cloud regions
- Real-time progress updates
- Ping, packet loss, and connection time testing
- Comprehensive scoring system
- IP location display
- Responsive table design