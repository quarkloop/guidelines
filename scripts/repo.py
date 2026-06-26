#!/usr/bin/env python3
"""
repo.py — Single entry point for quarkloop repository tooling.

Usage:
  python3 scripts/repo.py init --type library --name "Quark Lib" --target ./quark-lib
  python3 scripts/repo.py validate --repo /path/to/repo

This file is a thin entry point — all logic lives in scripts/src/.
"""

import sys
import os

# Add scripts/ to sys.path so we can import the src package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli import main

if __name__ == "__main__":
    main()
