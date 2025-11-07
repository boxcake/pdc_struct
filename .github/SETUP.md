# GitHub Actions Setup Guide

This repository includes three GitHub Actions workflows for automated testing and publishing.

## Workflows Overview

### 1. **test.yml** - Continuous Integration Testing
- **Triggers**: Push to `main` or `develop` branches, and all pull requests
- **What it does**:
  - Runs tests on multiple Python versions (3.10, 3.11, 3.12, 3.13)
  - Tests across multiple operating systems (Ubuntu, Windows, macOS)
  - Generates coverage reports
  - Uploads coverage to Codecov (optional)
  - Checks code formatting with Black
  - Lints code with Ruff

### 2. **test-build.yml** - Build Verification
- **Triggers**: Manual trigger or push to `main` when `pyproject.toml` changes
- **What it does**:
  - Builds the distribution packages (wheel and source)
  - Verifies package metadata with `twine check`
  - Tests installation from the built wheel
  - Runs basic import tests
  - Stores artifacts for inspection

### 3. **publish.yml** - PyPI Publishing
- **Triggers**: When a GitHub release is published
- **What it does**:
  - Builds distribution packages
  - Publishes to TestPyPI (for verification)
  - Publishes to PyPI (production)
  - Uses trusted publishing (no API tokens needed)

## Initial Setup

### Step 1: Enable GitHub Actions

GitHub Actions should be enabled by default. Verify in:
- Repository → Settings → Actions → General
- Ensure "Allow all actions and reusable workflows" is selected

### Step 2: Set Up PyPI Trusted Publishing

Trusted publishing is the modern, secure way to publish to PyPI without managing API tokens.

#### For PyPI (Production):

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in:
   - **PyPI Project Name**: `pdc_struct`
   - **Owner**: `boxcake`
   - **Repository name**: `pdc_struct`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
4. Click "Add"

#### For TestPyPI (Testing):

1. Go to https://test.pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in:
   - **PyPI Project Name**: `pdc_struct`
   - **Owner**: `boxcake`
   - **Repository name**: `pdc_struct`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `testpypi`
4. Click "Add"

**Note**: You need to create the pending publisher BEFORE your first release, as the project doesn't exist on PyPI yet.

### Step 3: Create GitHub Environments (Optional but Recommended)

For additional control and protection:

1. Go to: Repository → Settings → Environments
2. Create two environments:
   - **pypi**: For production releases
   - **testpypi**: For test releases
3. For the `pypi` environment, consider adding:
   - Required reviewers (to prevent accidental releases)
   - Deployment branches rule (only from `main`)

### Step 4: Set Up Codecov (Optional)

If you want coverage reports:

1. Go to https://codecov.io/
2. Sign in with GitHub
3. Add your repository
4. Copy the upload token (if needed)
5. Add to repository secrets: Settings → Secrets → Actions → New secret
   - Name: `CODECOV_TOKEN`
   - Value: Your token

**Note**: The current workflow will work without this setup; it will just skip the upload step.

## Usage

### Running Tests

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request

You can also manually trigger tests:
1. Go to: Actions → Tests
2. Click "Run workflow"

### Testing a Build

Before creating a release, test the build:

1. Go to: Actions → Test Build
2. Click "Run workflow"
3. Select the branch
4. Click "Run workflow"
5. Check the artifacts to verify the build

### Publishing a Release

1. **Ensure all tests pass** on the `main` branch

2. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.2.0"
   ```

3. **Update CHANGELOG.md**:
   - Move items from `[Unreleased]` to new version section
   - Add date and link

4. **Commit and push**:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 0.2.0"
   git push origin main
   ```

5. **Create a git tag**:
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```

6. **Create GitHub Release**:
   - Go to: Repository → Releases → Create a new release
   - Choose the tag you just created (v0.2.0)
   - Release title: `v0.2.0`
   - Description: Copy from CHANGELOG.md
   - Click "Publish release"

7. **Automatic Publishing**:
   - The `publish.yml` workflow will automatically trigger
   - It will publish to both TestPyPI and PyPI
   - Check: Actions → Publish to PyPI (to monitor progress)

## Troubleshooting

### Tests Failing

- Check the Actions tab for error details
- Run tests locally: `pytest --cov=pdc_struct`
- Ensure all dependencies are installed: `pip install -e ".[dev]"`

### Publish Workflow Failing

**"PyPI project not found"**:
- Ensure you've set up trusted publishing (see Step 2)
- The pending publisher must be created BEFORE the first release

**"Environment protection rules"**:
- Check if environment requires reviewers
- Approve the deployment in the Actions tab

**"Permission denied"**:
- Verify `id-token: write` permission is in workflow
- Check repository settings allow Actions to create tokens

### Build Failing

- Run locally: `python -m build`
- Check: `twine check dist/*`
- Verify `pyproject.toml` is valid
- Ensure all package files are included

## Manual Publishing (Fallback)

If you need to publish manually (not recommended):

```bash
# Install tools
pip install build twine

# Build
python -m build

# Check
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Best Practices

1. **Always test on TestPyPI first** before publishing to PyPI
2. **Use semantic versioning**: MAJOR.MINOR.PATCH
3. **Tag releases** with `v` prefix: `v0.1.0`
4. **Update CHANGELOG.md** before every release
5. **Run test-build workflow** before creating a release
6. **Never commit API tokens** (use trusted publishing instead)

## Security Notes

- This workflow uses **trusted publishing** - no API tokens needed
- Tokens are never stored in the repository
- PyPI verifies the workflow identity via OIDC
- Only releases from this repository can publish to your PyPI project
