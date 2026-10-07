#!/usr/bin/env python3
"""Convenience launcher:  python main.py /path/to/java/project -o knowledgeFile.md"""
import sys

from knowledge_gen.cli import main

if __name__ == "__main__":
    sys.exit(main())
