#!/usr/bin/env python3
"""
Main entry point for the Career Path Finder application
"""

from .career_finder import CareerFinder

def main():
    """Main entry point for the application"""
    app = CareerFinder()
    app.run()

if __name__ == "__main__":
    main()
