#!/usr/bin/env python3
"""
Wrapper script for Monarch Money MCP Enhanced server.
Automatically installs dependencies if needed.
"""
import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies if not available."""
    required_packages = [
        'monarchmoney-enhanced>=0.11.0',
        'mcp>=1.9.4',
        'pydantic>=2.0.0',
        'httpx>=0.24.0',
        'anyio>=3.6.0'
    ]

    for package in required_packages:
        try:
            # Try to import the package to see if it's installed
            if 'monarchmoney' in package:
                import monarchmoney  # noqa
            elif 'mcp' in package:
                import mcp  # noqa
            elif 'pydantic' in package:
                import pydantic  # noqa
            elif 'httpx' in package:
                import httpx  # noqa
            elif 'anyio' in package:
                import anyio  # noqa
        except ImportError:
            # Package not found, install it
            print(f"Installing {package}...", file=sys.stderr)
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', '--user', '-q', package
                ], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                print(f"Successfully installed {package}", file=sys.stderr)
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to install {package}: {e}", file=sys.stderr)
                # Continue anyway, maybe it's already installed differently
                pass

def main():
    """Main entry point."""
    # Install dependencies first
    install_dependencies()

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Import and run the actual server
    try:
        with open('server.py', 'r') as f:
            server_code = f.read()
        exec(server_code, {'__name__': '__main__'})
    except Exception as e:
        print(f"Error running server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()