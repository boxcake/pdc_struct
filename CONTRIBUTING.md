# Contributing to PDC Struct

Thank you for your interest in contributing to PDC Struct! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs. **actual behavior**
- **Code samples** if applicable
- **Python version** and **Pydantic version**
- **Operating system** and version

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** for the enhancement
- **Expected behavior** and benefits
- **Code examples** if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Add tests** for any new functionality
4. **Ensure all tests pass** (`pytest`)
5. **Update documentation** as needed
6. **Update CHANGELOG.md** under the `[Unreleased]` section
7. **Submit your pull request**

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip or poetry for package management

### Setting Up Your Development Environment

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pdc_struct.git
   cd pdc_struct
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests to verify your setup:
   ```bash
   pytest
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=pdc_struct --cov-report=html

# Run specific test file
pytest tests/test_basic.py

# Run tests matching a pattern
pytest -k "test_bitfield"
```

### Code Style

This project uses:
- **Black** for code formatting
- **Ruff** for linting

Format your code before committing:

```bash
# Format code
black pdc_struct tests

# Run linter
ruff check pdc_struct tests
```

### Type Hints

- Use type hints for all function signatures
- Leverage Pydantic models for data validation
- Keep type annotations clear and maintainable

### Documentation

- Update docstrings for any new or modified functions
- Use clear, descriptive variable and function names
- Add comments for complex logic
- Update README.md if adding user-facing features
- Update CHANGELOG.md with your changes

## Project Structure

```
pdc_struct/
├── pdc_struct/           # Main package
│   ├── models/          # Core model classes
│   ├── type_handler/    # Type-specific handlers
│   ├── c_types.py       # C-compatible types
│   ├── enums.py         # Enumerations
│   ├── exc.py           # Custom exceptions
│   └── ...
├── tests/               # Test suite
├── examples/            # Example code
└── docs/                # Documentation
```

## Commit Message Guidelines

Write clear, descriptive commit messages:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when applicable

Examples:
```
Add support for nested BitFields

Fix byte order handling in IPv6Address serialization (#42)

Update documentation for StructConfig parameters
```

## Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Move unreleased changes in `CHANGELOG.md` to new version section
3. Create a git tag: `git tag -a v0.x.x -m "Release v0.x.x"`
4. Push tag: `git push origin v0.x.x`
5. Build and publish to PyPI:
   ```bash
   python -m build
   twine upload dist/*
   ```

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Test edge cases and boundary conditions

### Test Coverage

- Aim for high test coverage (>90%)
- All new features should include tests
- Bug fixes should include regression tests

## Questions?

Feel free to open an issue for questions or discussions about contributing.

## License

By contributing to PDC Struct, you agree that your contributions will be licensed under the MIT License.
