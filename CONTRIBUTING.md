# Spout Development

## Setup

```bash
# Clone the repository
git clone https://github.com/jameslford/spout.git
cd spout

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=spout --cov-report=html

# Run specific test file
pytest tests/test_core.py
```

## Code Quality

```bash
# Format code
black src tests examples

# Sort imports
isort src tests examples

# Type checking
mypy src

# Lint
flake8 src tests examples
```

## Project Structure

```
spout/
├── src/spout/              # Main package
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # Command line interface
│   ├── core.py             # Core functionality
│   ├── models/             # Data models
│   │   ├── __init__.py
│   │   ├── endpoint.py     # Endpoint models
│   │   └── framework.py    # Framework models
│   ├── framework_detectors/ # Framework detection
│   │   ├── __init__.py
│   │   ├── base.py         # Base detector class
│   │   ├── fastapi.py      # FastAPI detector
│   │   └── django_ninja.py # Django Ninja detector
│   └── generators/         # Client generators
│       ├── __init__.py
│       ├── base.py         # Base generator class
│       ├── fetch.py        # Fetch client generator
│       └── axios.py        # Axios client generator
├── tests/                  # Test files
├── examples/               # Example applications
└── docs/                   # Documentation
```

## Adding New Framework Support

1. Create a new detector in `src/spout/framework_detectors/`
2. Inherit from `BaseFrameworkDetector`
3. Implement `detect()` and `parse()` methods
4. Add to the `DETECTORS` list in `framework_detectors/detection_service.py`
5. Add tests in `tests/`

## Adding New Client Generators

1. Create a new generator in `src/spout/generators/`
2. Inherit from `BaseClientGenerator`
3. Implement `generate()` method
4. Add to the `GENERATORS` dict in `__init__.py`
5. Add tests in `tests/`