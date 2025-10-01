"""Simple example script showing basic Spout usage."""

from pathlib import Path
from spout import SpoutGenerator


def main():
    """Demonstrate basic Spout functionality."""
    print("🚀 Spout - TypeScript Client Generator")
    print("=" * 40)

    # Initialize generator
    generator = SpoutGenerator()

    # Example: Detect framework in examples directory
    examples_path = Path("examples")
    if examples_path.exists():
        print(f"\nChecking for frameworks in: {examples_path}")

        framework_info = generator.detect_framework(examples_path)
        if framework_info:
            print(f"✅ Found: {framework_info.name}")
            print(f"   Confidence: {framework_info.confidence:.2f}")
            print(f"   Files: {len(framework_info.detected_files)}")

            # Parse endpoints
            endpoints = generator.parse_endpoints(examples_path, framework_info)
            print(f"   Endpoints: {len(endpoints)}")

            if endpoints:
                print("\n📍 Discovered endpoints:")
                for endpoint in endpoints[:3]:  # Show first 3
                    print(
                        f"   {endpoint.method.value} {endpoint.path} -> {endpoint.function_name}"
                    )

                # Generate a sample client
                print("\n🔧 Generating TypeScript client (fetch)...")
                client_code = generator.generate_client(
                    endpoints=endpoints,
                    client_type="fetch",
                    base_url="https://api.example.com",
                )

                # Show a snippet
                lines = client_code.split("\n")
                print("📄 Generated client preview:")
                print("   " + "\n   ".join(lines[:10]))
                print("   ...")
                print(f"   Total lines: {len(lines)}")
        else:
            print("❌ No supported framework found")
    else:
        print("❌ Examples directory not found")

    print("\n💡 Try running:")
    print("   spout detect --input ./examples")
    print("   spout generate --input ./examples --output client.ts --client-type fetch")


if __name__ == "__main__":
    main()
