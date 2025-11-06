#!/usr/bin/env python3
"""
A cross-platform script to manage the UMS Store API project.
Replaces the functionality of run and setup.sh scripts.
"""

import os
import subprocess
import sys

# ANSI color codes
COLORS = {
    'RED': '\033[0;31m',
    'GREEN': '\033[0;32m',
    'YELLOW': '\033[1;33m',
    'NC': '\033[0m'  # No Color
}

def color_print(text: str, color: str) -> None:
    """Print colored text to the console."""
    print(f"{COLORS.get(color, '')}{text}{COLORS['NC']}")

def run_command(command: list[str], cwd: str | None = None) -> int:
    """Run a shell command and return the exit code."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd or os.getcwd(),
            check=True,
            shell=os.name == 'nt'  # Use shell=True on Windows for better command handling
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        color_print(f"Error running command: {' '.join(e.cmd)}", 'RED')
        color_print(str(e), 'RED')
        return e.returncode
    except Exception as e:
        color_print(f"Unexpected error: {str(e)}", 'RED')
        return 1

def show_help() -> None:
    """Display help message."""
    color_print("Usage: python run.py [command]", 'YELLOW')
    print("\nAvailable commands:")
    print("  runserver      - Start the development server")
    print("  lint           - Run linter")
    print("  lint-fix       - Fix linting issues")
    print("  install        - Install dependencies")
    print("  makemigrations - Make migrations")
    print("  migrate        - Migrate database")
    print("  setup          - Setup the project")
    print("  help           - Show this help message")

def setup_project() -> int:
    """Set up the project (replaces setup.sh)."""
    color_print("Setting up the project...", 'YELLOW')
    
    # Install dependencies
    color_print("Installing dependencies...", 'YELLOW')
    if run_command(["poetry", "install"]) != 0:
        return 1
    
    # Run database migrations
    color_print("Running database migrations...", 'YELLOW')
    if run_command(["poetry", "run", "python", "manage.py", "migrate"]) != 0:
        return 1
    
    # Create default admin account
    color_print("Creating default admin account...", 'YELLOW')
    if run_command(["poetry", "run", "python", "manage.py", "createadmin"]) != 0:
        return 1
    
    color_print("Setup complete.", 'GREEN')
    return 0

def main() -> int:
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        show_help()
        return 0

    command = sys.argv[1].lower()
    
    if command == 'runserver':
        return run_command(["poetry", "run", "python", "manage.py", "runserver"])
    elif command == 'lint':
        return run_command(["poetry", "run", "ruff", "check", "."])
    elif command == 'lint-fix':
        return run_command(["poetry", "run", "ruff", "check", ".", "--fix"])
    elif command == 'install':
        return run_command(["poetry", "install"])
    elif command == 'makemigrations':
        return run_command(["poetry", "run", "python", "manage.py", "makemigrations"])
    elif command == 'migrate':
        return run_command(["poetry", "run", "python", "manage.py", "migrate"])
    elif command == 'setup':
        return setup_project()
    elif command in ('help', '--help', '-h'):
        show_help()
        return 0
    else:
        color_print(f"Unknown command: {command}", 'RED')
        show_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
