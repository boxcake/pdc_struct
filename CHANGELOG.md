# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

*No changes yet*

---

## [1.0.0] - 2026-01-15

### Added
- Comprehensive BitFieldHandler tests (91% code coverage achieved)
- PyPI packaging configuration with automated publishing workflow
- Development dependencies (pytest, pytest-cov, black, ruff)
- Enhanced PyPI classifiers and keywords
- CONTRIBUTING.md guidelines
- ROADMAP.md for future development planning
- Codecov integration for test coverage tracking
- Automated test workflows for Python 3.11, 3.12, and 3.13
- Comprehensive API reference documentation with mkdocstrings auto-generation
- Expanded docstrings with usage examples for all public classes and methods:
  - `StructModel`: `to_bytes()`, `from_bytes()`, `clone()` with round-trip examples
  - `StructConfig`: Full parameter documentation with Args section
  - `BitFieldModel`: `Bit()` function and `packed_value` property examples
  - `ByteOrder` and `HeaderFlags` enums with format details
  - Fixed-width types (`Int8`, `UInt8`, `Int16`, `UInt16`) with usage examples
- Contextual introductions in all API reference pages
- Security scanning with bandit and pip-audit in CI
- Python 3.14-dev experimental testing in CI

### Changed
- **BREAKING**: Minimum Python version raised from 3.10 to 3.11 (required for StrEnum support)
- **Package name:** Changed PyPI package name from `pdc_struct` to `pdc-struct` (import remains `import pdc_struct`)
- Improved code quality and removed debug print statements
- Enhanced .gitignore to explicitly exclude .pyc and .pyo files
- Optimized CI test matrix (removed macOS, kept Ubuntu + Windows)

### Fixed
- YAML syntax errors in GitHub Actions workflows
- Codecov action updated to v5 with proper authentication
- Black formatting applied consistently across all files
- Removed binary .pyc files from git history
- Cross-platform docs: replaced symlinks with snippets for Windows compatibility

---

## [0.1.0] - 2026-01-07

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

---

[Unreleased]: https://github.com/boxcake/pdc_struct/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/boxcake/pdc_struct/releases/tag/v1.0.0
[0.1.0]: https://github.com/boxcake/pdc_struct/releases/tag/v0.1.0
