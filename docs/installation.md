# Installation

## Requirements

- **Python**: 3.11 or higher
- **Pydantic**: 2.0 or higher

## Install from PyPI

The recommended way to install PDC Struct:

```bash
pip install pdc-struct
```

## Install from Source

For the latest development version:

```bash
pip install git+https://github.com/boxcake/pdc_struct.git
```

## Install for Development

If you want to contribute:

```bash
git clone https://github.com/boxcake/pdc_struct.git
cd pdc_struct
pip install -e ".[dev]"
```

This installs the package in editable mode with all development dependencies including:

- `pytest` and `pytest-cov` for testing
- `black` for code formatting
- `ruff` for linting
- `mkdocs-material` for documentation

## Verify Installation

```python
import pdc_struct
print(pdc_struct.__version__)  # Should print: 1.0.0
```

## Optional Dependencies

### Documentation

To build the documentation locally:

```bash
pip install pdc-struct[docs]
mkdocs serve
```

### Testing

To run tests:

```bash
pip install pdc-struct[test]
pytest
```

## Troubleshooting

### ImportError: No module named 'pydantic'

PDC Struct requires Pydantic 2.0+. Install it:

```bash
pip install "pydantic>=2.0.0"
```

### Python Version Error

Ensure you're using Python 3.11 or higher:

```bash
python --version
```

If needed, create a virtual environment with the correct Python version.

## Next Steps

Continue to [Quick Start](getting-started.md) to create your first struct!
