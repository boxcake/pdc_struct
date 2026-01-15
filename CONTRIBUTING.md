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

We follow a structured branching workflow:

- **Feature branches** → merge to `dev`
- **dev** → merge to `main` for releases
- **main** → production-ready code only

**Pull Request Process:**

1. **Fork the repository** and create your feature branch from `dev`
   ```bash
   git checkout dev
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** following the code style guidelines
3. **Add tests** for any new functionality
4. **Ensure all tests pass** (`pytest`)
5. **Update documentation** as needed
6. **Update CHANGELOG.md** under the `[Unreleased]` section
7. **Submit your pull request** targeting the `dev` branch
8. **Wait for CI checks** - all tests and linting must pass
9. Once approved, your PR will be merged to `dev`

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip for package management

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

Releases are automatically published to PyPI via GitHub Actions when a release is created.

### Creating a Release

1. **Ensure `dev` is ready for release**
   - All features merged and tested
   - CI passing on `dev` branch

2. **Merge `dev` to `main`**
   ```bash
   git checkout main
   git merge dev
   ```

3. **Update version and changelog**
   - Update version in `pyproject.toml` and `pdc_struct/__init__.py`
   - Move `[Unreleased]` changes in `CHANGELOG.md` to new version section with date
   - Commit changes:
     ```bash
     git add pyproject.toml pdc_struct/__init__.py CHANGELOG.md
     git commit -m "Release vX.Y.Z"
     ```

4. **Push to main**
   ```bash
   git push origin main
   ```

5. **Create GitHub Release**
   - Go to: https://github.com/boxcake/pdc_struct/releases/new
   - Tag: `vX.Y.Z` (e.g., `v1.0.0`)
   - Target: `main` branch
   - Title: `vX.Y.Z - Release Name`
   - Description: Copy relevant section from CHANGELOG.md
   - Click "Publish release"

6. **Automated Publishing**
   - GitHub Actions will automatically:
     - Build the distribution packages
     - Run final validation checks
     - Publish to TestPyPI
     - Publish to PyPI
   - Monitor the workflow at: https://github.com/boxcake/pdc_struct/actions

7. **Verify Publication**
   - Check PyPI: https://pypi.org/project/pdc-struct/
   - Test installation: `pip install pdc-struct`

### Hotfix Process

For urgent fixes to production:

1. Create hotfix branch from `main`:
   ```bash
   git checkout -b hotfix/issue-description main
   ```
2. Make the fix and commit
3. Create PR targeting `main`
4. After merge, follow release process above
5. Merge `main` back to `dev` to sync changes

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
