"""Example usage scripts for Spout."""

# Example 1: Basic usage with FastAPI
# spout generate --input ./examples --output ./client.ts --client-type fetch

# Example 2: Generate axios client with base URL
# spout generate --input ./my_fastapi_app --output ./src/api/client.ts --client-type axios --base-url https://api.example.com

# Example 3: Use configuration file
# spout generate --input ./my_project --output ./generated/client.ts --config ./spout.config.json

# Example 4: Detect framework only
# spout detect --input ./my_project

# Example 5: List available generators
# spout list-generators
