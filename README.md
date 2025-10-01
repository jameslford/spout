# Spout

Generate TypeScript clients from Python web frameworks with typed responses.

## Overview

Spout automatically detects Python web frameworks (FastAPI, Django Ninja, etc.) that enforce typed responses and generates corresponding TypeScript clients. It supports multiple client types including fetch, axios, and more.

## Features

- 🔍 **Framework Detection**: Automatically detects FastAPI, Django Ninja, and other typed frameworks
- 📝 **Type Generation**: Generates accurate TypeScript types from Python type annotations
- 🌐 **Multiple Clients**: Support for fetch, axios, and other HTTP client libraries
- ⚡ **CLI Interface**: Easy-to-use command-line interface
- 🔧 **Configurable**: Customize output format and client options

## Installation

```bash
pip install spout
```

## Quick Start

```bash
# Generate a fetch-based TypeScript client
spout generate --input ./my_app --output ./client.ts --client-type fetch

# Generate an axios-based client with custom configuration
spout generate --input ./my_app --output ./client.ts --client-type axios --config ./spout.config.json
```

## Supported Frameworks

- [FastAPI](https://fastapi.tiangolo.com/)
- [Django Ninja](https://django-ninja.rest-framework.com/)
- More frameworks coming soon!

## Client Types

- `fetch` - Modern browser fetch API
- `axios` - Popular HTTP client library
- `xhr` - XMLHttpRequest-based client
- More client types planned

## Configuration

Create a `spout.config.json` file in your project root:

```json
{
  "clientType": "fetch",
  "outputPath": "./generated/client.ts",
  "includeTypes": true,
  "baseUrl": "https://api.example.com",
  "authMethod": "bearer"
}
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
isort src tests

# Type checking
mypy src
```

## License

MIT License - see LICENSE file for details.
