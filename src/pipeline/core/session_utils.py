#!/usr/bin/env python3
"""
Unified session management for BeAScout pipelines
Ensures consistent timestamps across development, regression, and production workflows
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO
import contextlib


class SessionManager:
    """Manages session timestamps and file naming across all pipelines"""

    def __init__(self, session_id: Optional[str] = None, session_type: str = "pipeline"):
        """
        Initialize session manager
        Args:
            session_id: Optional existing session ID (YYYYMMDD_HHMMSS format)
            session_type: Type of session (pipeline, regression, development)
        """
        self.session_id = session_id if session_id else self._generate_session_id()
        self.session_type = session_type
        self.start_time = datetime.now()

    def _generate_session_id(self) -> str:
        """Generate new session ID with consistent format"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_timestamped_filename(self, base_name: str, extension: str = None) -> str:
        """Generate filename with session timestamp"""
        if extension:
            return f"{base_name}_{self.session_id}.{extension}"
        else:
            return f"{base_name}_{self.session_id}"

    def get_log_filename(self, script_name: str) -> str:
        """Generate standardized log filename"""
        return f"{script_name}_{self.session_id}.log"

    def get_log_path(self, script_name: str) -> Path:
        """Get full log file path"""
        return Path("data/logs") / self.get_log_filename(script_name)

    def add_session_args(self, parser: argparse.ArgumentParser):
        """Add standard session arguments to argument parser"""
        parser.add_argument('--session-id', type=str,
                          help='Session timestamp (YYYYMMDD_HHMMSS) for file correlation')
        parser.add_argument('--session-type', type=str, default='pipeline',
                          choices=['pipeline', 'regression', 'development'],
                          help='Type of pipeline session')
        parser.add_argument('--log', action='store_true',
                          help='Direct stdout/stderr to log file')
        parser.add_argument('--verbose', action='store_true',
                          help='Output full debug messages')

    @classmethod
    def from_args(cls, args):
        """Create SessionManager from parsed arguments"""
        session_type = getattr(args, 'session_type', 'pipeline')
        return cls(session_id=args.session_id, session_type=session_type)

    def terse_print(self, *args, **kwargs):
        """Print to terminal only when in terminal_terse mode, otherwise normal print"""
        if hasattr(self, '_terse_manager'):
            self._terse_manager.terse_print(*args, **kwargs)
        else:
            print(*args, **kwargs)

    def log_and_terse_print(self, *args, **kwargs):
        """Print to both log file and terminal when in terminal_terse mode"""
        if hasattr(self, '_terse_manager'):
            # Print to terminal using terse_print
            self._terse_manager.terse_print(*args, **kwargs)
            # Also print to log file (redirected stdout)
            print(*args, **kwargs)
        else:
            # Normal mode - just print normally
            print(*args, **kwargs)


class LogRedirector:
    """Context manager for redirecting stdout/stderr to log files"""

    def __init__(self, log_path: Path, verbose: bool = False):
        """
        Initialize log redirector
        Args:
            log_path: Path to log file
            verbose: If True, also output to terminal
        """
        self.log_path = log_path
        self.verbose = verbose
        self.log_file = None
        self.original_stdout = None
        self.original_stderr = None

        # Ensure log directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def __enter__(self):
        """Start log redirection"""
        self.log_file = open(self.log_path, 'w', encoding='utf-8')
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        if self.verbose:
            # Tee output - write to both file and terminal
            sys.stdout = TeeOutput(self.original_stdout, self.log_file)
            sys.stderr = TeeOutput(self.original_stderr, self.log_file)
        else:
            # Redirect only to file
            sys.stdout = self.log_file
            sys.stderr = self.log_file

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End log redirection"""
        if self.original_stdout:
            sys.stdout = self.original_stdout
        if self.original_stderr:
            sys.stderr = self.original_stderr
        if self.log_file:
            self.log_file.close()


class TeeOutput:
    """Write to multiple outputs simultaneously"""

    def __init__(self, *outputs):
        self.outputs = outputs

    def write(self, data):
        for output in self.outputs:
            output.write(data)
            output.flush()

    def flush(self):
        for output in self.outputs:
            output.flush()


class TerseTerminalManager:
    """Manages terminal_terse mode where scripts can selectively output to terminal"""

    def __init__(self, log_file):
        self.log_file = log_file
        self.original_stdout = None
        self.original_stderr = None

    def __enter__(self):
        """Start terse terminal mode"""
        import sys
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        # Redirect all output to log file only
        sys.stdout = self.log_file
        sys.stderr = self.log_file

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End terse terminal mode"""
        import sys
        if self.original_stdout:
            sys.stdout = self.original_stdout
        if self.original_stderr:
            sys.stderr = self.original_stderr

    def terse_print(self, *args, **kwargs):
        """Print to terminal only (bypassing log redirection)"""
        if self.original_stdout:
            print(*args, **kwargs, file=self.original_stdout)
        else:
            print(*args, **kwargs)


@contextlib.contextmanager
def session_logging(session_manager: SessionManager, script_name: str,
                   log_enabled: bool = False, verbose: bool = False, terminal_terse: bool = False):
    """
    Context manager for session-aware logging

    Args:
        session_manager: SessionManager instance
        script_name: Name of the script for log filename
        log_enabled: Whether to redirect to log file
        verbose: Whether to show output on terminal when logging
        terminal_terse: If True, terminal gets terse output while log gets full output
    """
    if log_enabled:
        log_path = session_manager.get_log_path(script_name)
        print(f"📄 Logging to: {log_path}")

        if terminal_terse:
            # Special mode: All output goes to log, but scripts can use terse_print for terminal
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'w', encoding='utf-8') as log_file:
                with TerseTerminalManager(log_file) as terse_manager:
                    # Attach the terse_manager to session_manager for script access
                    session_manager._terse_manager = terse_manager
                    yield session_manager
                    # Clean up the reference
                    if hasattr(session_manager, '_terse_manager'):
                        delattr(session_manager, '_terse_manager')
        else:
            # Standard logging behavior
            log_verbose = verbose
            with LogRedirector(log_path, verbose=log_verbose):
                yield session_manager
    else:
        yield session_manager


def setup_script_session(script_name: str) -> tuple[SessionManager, bool, bool]:
    """
    Standard setup for pipeline scripts with session management

    Returns:
        tuple: (session_manager, log_enabled, verbose)
    """
    parser = argparse.ArgumentParser(description=f"BeAScout {script_name}")

    # Add session arguments
    session_manager = SessionManager()
    session_manager.add_session_args(parser)

    # Parse arguments
    args, remaining = parser.parse_known_args()

    # Create session manager from args
    if args.session_id:
        session_manager = SessionManager.from_args(args)

    return session_manager, args.log, args.verbose