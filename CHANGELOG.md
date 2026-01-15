# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-07

### Added
- Initial public release of PDC Struct
- `StructModel` base class for binary-serializable Pydantic models
- `StructConfig` for configuring packing/unpacking behavior
- Two operating modes:
  - C_COMPATIBLE mode for C struct interoperability
  - DYNAMIC mode for flexible Python-to-Python communication
- Comprehensive type support:
  - Fixed-width integer types (Int8, UInt8, Int16, UInt16, Int32, UInt32, Int64, UInt64)
  - Standard Python types (int, float, bool, str, bytes)
  - Enums (IntEnum and StrEnum)
  - UUID type support
  - IP address types (IPv4Address, IPv6Address)
- BitField support for efficient bit-level data packing
- Nested StructModel support
- Configurable byte order (little-endian, big-endian, native)
- String handling with fixed and variable lengths
- Optional field support
- Custom exceptions: `StructPackError` and `StructUnpackError`
- Comprehensive test suite with 15 test modules
- Example implementations:
  - ARP packet decoder
  - Python-C interprocess communication examples

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

---

## [1.0.0] - 2025-01-15

### Added
- Comprehensive BitFieldHandler tests (91% code coverage achieved)
- PyPI packaging configuration with automated publishing workflow
- Development dependencies (pytest, pytest-cov, black, ruff)
- Enhanced PyPI classifiers and keywords
- CONTRIBUTING.md guidelines
- ROADMAP.md for future development planning
- Codecov integration for test coverage tracking
- Automated test workflows for Python 3.11, 3.12, and 3.13

### Changed
- **BREAKING**: Minimum Python version raised from 3.10 to 3.11 (required for StrEnum support)
- Improved code quality and removed debug print statements
- Enhanced .gitignore to explicitly exclude .pyc and .pyo files

### Fixed
- YAML syntax errors in GitHub Actions workflows
- Codecov action updated to v5 with proper authentication
- Black formatting applied consistently across all files
- Removed binary .pyc files from git history

---

## [Unreleased]

### Added
- TBD

[1.0.0]: https://github.com/boxcake/pdc_struct/releases/tag/v1.0.0
[0.1.0]: https://github.com/boxcake/pdc_struct/releases/tag/v0.1.0
[Unreleased]: https://github.com/boxcake/pdc_struct/compare/v1.0.0...HEAD
