#!/usr/bin/env python3
"""Debug script to check .env file loading."""

import os
from pathlib import Path

def check_env_file():
    """Check if .env file exists and can be loaded."""
    env_file = Path(".env")

    print(f"🔍 Checking environment file...")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Looking for .env at: {env_file.absolute()}")

    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please create .env file from .env.example:")
        print("  cp .env.example .env")
        print("  # Then edit .env with your credentials")
        return False

    print("✅ .env file found")
    print(f"File size: {env_file.stat().st_size} bytes")

    # Read and parse .env file
    print("\n📄 .env file contents:")
    found_email = False
    found_password = False

    with open(env_file) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key, value = line.split('=', 1)
                value = value.strip('"\'')

                if key == "MONARCH_EMAIL":
                    found_email = True
                    print(f"   Line {line_num}: {key}={value}")
                elif key == "MONARCH_PASSWORD":
                    found_password = True
                    print(f"   Line {line_num}: {key}={'*' * len(value)}")
                elif key == "MONARCH_MFA_SECRET":
                    print(f"   Line {line_num}: {key}={'*' * len(value) if value else '(empty)'}")
                else:
                    print(f"   Line {line_num}: {key}={value}")

                # Set in environment
                os.environ[key] = value
            else:
                print(f"   Line {line_num}: (invalid format) {line}")

    print(f"\n✅ Found email: {found_email}")
    print(f"✅ Found password: {found_password}")

    # Check environment variables after loading
    print(f"\n🔍 Environment variables after loading:")
    print(f"   MONARCH_EMAIL: {os.getenv('MONARCH_EMAIL', '(not set)')}")
    print(f"   MONARCH_PASSWORD: {'*' * len(os.getenv('MONARCH_PASSWORD', '')) if os.getenv('MONARCH_PASSWORD') else '(not set)'}")
    print(f"   MONARCH_MFA_SECRET: {'*' * len(os.getenv('MONARCH_MFA_SECRET', '')) if os.getenv('MONARCH_MFA_SECRET') else '(not set)'}")

    if found_email and found_password:
        print("\n✅ Required credentials found!")
        return True
    else:
        print("\n❌ Missing required credentials!")
        print("Make sure your .env file contains:")
        print("  MONARCH_EMAIL=your-email@example.com")
        print("  MONARCH_PASSWORD=your-password")
        return False

if __name__ == "__main__":
    success = check_env_file()
    exit(0 if success else 1)