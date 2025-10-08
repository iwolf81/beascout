#!/usr/bin/env python3
"""
BeAScout Regression Test Runner

Comprehensive regression testing framework that validates all pipeline components
against reference data to catch regressions during development.

Features:
- Unit processing regression test (HNE unit extraction)
- Three-way validation regression test (unit presence correlation)
- Excel report regression test (commissioner report generation)
- Discarded units regression test (territory filtering validation)
- Clear pass/fail reporting with detailed diagnostics

Usage:
    python tests/run_regression_tests.py              # Run all tests
    python tests/run_regression_tests.py --unit-only  # Run unit processing only
    python tests/run_regression_tests.py --verbose    # Detailed output
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import tempfile
import json
from typing import Dict, List, Tuple, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.core.session_utils import SessionManager, session_logging


class RegressionTestRunner:
    """Comprehensive regression test framework for BeAScout pipeline"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.project_root = Path(__file__).parent.parent
        self.results = []
        self.temp_dirs = []

        # Initialize session management
        self.session_manager = SessionManager(session_type='regression')
        self.generated_files = []  # Track all generated files for final summary

        import time
        self.test_start_time = time.time()  # Track when test started for debug file collection

        # Sequential pipeline steps with fail-fast execution
        self.pipeline_steps = [
            {
                'name': 'Process Full Dataset',
                'description': 'Execute process_full_dataset.py on reference HTML data',
                'command': self._run_process_full_dataset_step,
                'step_number': 1
            },
            {
                'name': 'Unit Processing Regression Test (udiff)',
                'description': 'Validate HNE unit extraction debug output',
                'command': self._run_udiff_test,
                'step_number': 2
            },
            {
                'name': 'Three-Way Validation',
                'description': 'Execute three_way_validator.py on processed data',
                'command': self._run_three_way_validator_step,
                'step_number': 3
            },
            {
                'name': 'Three-Way Validation Regression Test (vdiff)',
                'description': 'Validate unit correlation debug output',
                'command': self._run_vdiff_test,
                'step_number': 4
            },
            {
                'name': 'Generate Commissioner Report',
                'description': 'Execute generate_commissioner_report.py',
                'command': self._run_generate_report_step,
                'step_number': 5
            },
            {
                'name': 'Excel Report Regression Test (ediff)',
                'description': 'Validate commissioner report generation',
                'command': self._run_ediff_test,
                'step_number': 6
            }
        ]

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "ERROR":
            print(f"❌ [{timestamp}] {message}")
        elif level == "WARN":
            print(f"⚠️  [{timestamp}] {message}")
        elif level == "SUCCESS":
            print(f"✅ [{timestamp}] {message}")
        else:
            print(f"ℹ️  [{timestamp}] {message}")

    def _check_prerequisites(self) -> bool:
        """Check that reference data and tools are available"""
        self.log("Checking prerequisites...")

        missing_files = []

        # Check reference files needed for regression tests
        required_files = [
            'tests/reference/units/unit_identifier_debug_scraped_reference_u.log',
            'tests/reference/reports/cross_reference_validation_debug_reference.log',
            'tests/reference/reports/BeAScout_Quality_Report_anonymized.xlsx',
            'tests/reference/key_three/anonymized_key_three.json',
            'tests/tools/compare_excel_files.py'
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(str(full_path))

        # Check required reference directories
        required_dirs = [
            'tests/reference/units/scraped',
            'tests/reference/key_three'
        ]

        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_files.append(f"Directory: {full_path}")

        if missing_files:
            self.log("Missing required reference files:", "ERROR")
            for file_path in missing_files:
                self.log(f"  - {file_path}", "ERROR")
            return False

        self.log("✓ All prerequisite files found")
        return True

    def _run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
        """Run shell command and return exit code, stdout, stderr"""
        if cwd is None:
            cwd = self.project_root

        if self.verbose:
            self.log(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out after 5 minutes"
        except Exception as e:
            return -1, "", str(e)

    def _run_process_full_dataset_step(self) -> Dict:
        """Execute process_full_dataset.py pipeline step"""
        self.log("Executing process_full_dataset.py...")

        cmd = [
            'python3', '-u', 'src/pipeline/processing/process_full_dataset.py',
            'tests/reference/units/scraped/',
            '--session-id', self.session_manager.session_id,
            '--log'
        ]

        if self.verbose:
            cmd.append('--verbose')

        exit_code, stdout, stderr = self._run_command(cmd)

        # Always show output for pipeline steps (verbose or not)
        if stdout:
            self.log("Pipeline STDOUT:")
            for line in stdout.strip().split('\n'):
                if line.strip():
                    self.log(f"  {line}")

        if stderr:
            self.log("Pipeline STDERR:")
            for line in stderr.strip().split('\n'):
                if line.strip():
                    self.log(f"  {line}")

        if exit_code != 0:
            return {
                'passed': False,
                'error': f"Process full dataset failed with exit code {exit_code}",
                'details': f"STDERR: {stderr}\nSTDOUT: {stdout}"
            }

        # Verify the output file was created
        output_file = self.project_root / 'data/raw/all_units_comprehensive_scored.json'
        if not output_file.exists():
            return {
                'passed': False,
                'error': 'Expected output file not created',
                'details': f'Expected file: {output_file}'
            }

        # Show debug files created
        debug_files = list(self.project_root.glob('data/debug/unit_identifier_debug_scraped_*.log'))
        if debug_files:
            latest_debug = max(debug_files, key=lambda x: x.stat().st_mtime)
            self.log(f"Debug log generated: {latest_debug.name}")

        return {'passed': True, 'details': 'Pipeline step 1 completed successfully'}

    def _run_three_way_validator_step(self) -> Dict:
        """Execute three_way_validator.py pipeline step"""
        self.log("Executing three_way_validator.py...")

        # CRITICAL: Use regression output path to prevent contaminating production data
        regression_output = 'data/output/regression/enhanced_three_way_validation_results.json'

        cmd = [
            'python3', '-u', 'src/pipeline/analysis/three_way_validator.py',
            '--key-three', 'tests/reference/key_three/anonymized_key_three.json',
            '--scraped-data', 'data/raw/all_units_comprehensive_scored.json',
            '--output', regression_output,
            '--session-id', self.session_manager.session_id,
            '--log'
        ]

        if self.verbose:
            cmd.append('--verbose')

        exit_code, stdout, stderr = self._run_command(cmd)

        # Always show output for pipeline steps (verbose or not)
        if stdout:
            self.log("Pipeline STDOUT:")
            for line in stdout.strip().split('\n'):
                if line.strip():
                    self.log(f"  {line}")

        if stderr:
            self.log("Pipeline STDERR:")
            for line in stderr.strip().split('\n'):
                if line.strip():
                    self.log(f"  {line}")

        if exit_code != 0:
            return {
                'passed': False,
                'error': f"Three-way validator failed with exit code {exit_code}",
                'details': f"STDERR: {stderr}\nSTDOUT: {stdout}"
            }

        # Verify the output file was created in regression path
        output_file = self.project_root / regression_output
        if not output_file.exists():
            return {
                'passed': False,
                'error': 'Expected validation results file not created',
                'details': f'Expected file: {output_file}'
            }

        # Show debug files created
        debug_files = list(self.project_root.glob('data/debug/cross_reference_validation_debug_*.log'))
        if debug_files:
            latest_debug = max(debug_files, key=lambda x: x.stat().st_mtime)
            self.log(f"Debug log generated: {latest_debug.name}")

        return {'passed': True, 'details': 'Pipeline step 2 completed successfully'}

    def _run_generate_report_step(self) -> Dict:
        """Execute generate_commissioner_report.py pipeline step"""
        self.log("Executing generate_commissioner_report.py...")

        # CRITICAL: Use regression paths to prevent contaminating production data
        regression_validation = 'data/output/regression/enhanced_three_way_validation_results.json'
        regression_reports_dir = 'data/output/regression/reports'

        cmd = [
            'python3', '-u', 'src/pipeline/analysis/generate_commissioner_report.py',
            '--key-three', 'tests/reference/key_three/anonymized_key_three.json',
            '--quality-data', 'data/raw/all_units_comprehensive_scored.json',
            '--validation-file', regression_validation,
            '--session-id', self.session_manager.session_id,
            '--output-dir', regression_reports_dir,
            '--log'
        ]

        exit_code, stdout, stderr = self._run_command(cmd)

        # Always show output for pipeline steps (verbose or not)
        if stdout:
            self.log("Pipeline STDOUT:")
            for line in stdout.strip().split('\n'):
                if line.strip():
                    self.log(f"  {line}")

        if stderr:
            self.log("Pipeline STDERR:")
            for line in stderr.strip().split('\n'):
                if line.strip():
                    self.log(f"  {line}")

        if exit_code != 0:
            return {
                'passed': False,
                'error': f"Report generation failed with exit code {exit_code}",
                'details': f"STDERR: {stderr}\nSTDOUT: {stdout}"
            }

        # Verify a report file was created in regression path
        report_pattern = f'{regression_reports_dir}/BeAScout_Quality_Report_*.xlsx'
        report_files = list(self.project_root.glob(report_pattern))
        if not report_files:
            return {
                'passed': False,
                'error': 'Expected Excel report file not created',
                'details': f'Expected files matching pattern: {report_pattern}'
            }

        # Show report file created
        latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
        self.log(f"Report generated: {latest_report.name}")

        return {'passed': True, 'details': 'Pipeline step 3 completed successfully'}

    def _run_udiff_test(self) -> Dict:
        """Run udiff test: Compare unit processing debug log with reference"""
        self.log("Validating unit processing debug output...")

        # Find the generated debug file
        debug_files = list(self.project_root.glob('data/debug/unit_identifier_debug_scraped_*.log'))
        if not debug_files:
            return {
                'passed': False,
                'error': "No unit identifier debug file found",
                'details': "Expected files in data/debug/ matching pattern unit_identifier_debug_scraped_*.log"
            }

        # Use the most recent debug file
        latest_debug = max(debug_files, key=lambda x: x.stat().st_mtime)

        # Create unique sorted file for comparison (like udiff alias)
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_u.log') as tmp_file:
            self.temp_dirs.append(tmp_file.name)
            sorted_file = tmp_file.name

            # Sort the debug file
            cmd = ['sort', '-u', str(latest_debug)]
            exit_code, stdout, stderr = self._run_command(cmd)

            if exit_code != 0:
                return {
                    'passed': False,
                    'error': "Failed to sort debug file",
                    'details': f"STDERR: {stderr}"
                }

            # Write sorted content to temp file
            tmp_file.write(stdout)
            tmp_file.flush()  # Ensure data is written

        # Verify temp file exists and show its path
        temp_path = Path(sorted_file)
        if not temp_path.exists():
            return {
                'passed': False,
                'error': 'Temp file was not created properly',
                'details': f'Expected temp file: {sorted_file}'
            }

        self.log(f"Sorted temp file: {sorted_file}")
        self.log(f"Temp file size: {temp_path.stat().st_size} bytes")

        # Compare with reference
        reference_file = self.project_root / 'tests/reference/units/unit_identifier_debug_scraped_reference_u.log'

        cmd = ['diff', str(reference_file), sorted_file]
        exit_code, stdout, stderr = self._run_command(cmd)

        # Show more detailed diff information
        if self.verbose:
            self.log(f"Diff exit code: {exit_code}")
            if stdout:
                self.log(f"Diff STDOUT:\n{stdout}")
            if stderr:
                self.log(f"Diff STDERR:\n{stderr}")

        if exit_code == 0:
            return {'passed': True, 'details': 'PASS: No differences with reference log'}
        else:
            return {
                'passed': False,
                'error': 'Unit processing regression detected',
                'details': f"Diff output:\n{stdout}\nDiff STDERR:\n{stderr}"
            }

    def _run_vdiff_test(self) -> Dict:
        """Run vdiff test: Compare three-way validation debug log with reference"""
        self.log("Validating three-way validation debug output...")

        # Find the generated debug file
        debug_files = list(self.project_root.glob('data/debug/cross_reference_validation_debug_*.log'))
        if not debug_files:
            return {
                'passed': False,
                'error': 'No validation debug file found',
                'details': 'Expected files in data/debug/ matching pattern cross_reference_validation_debug_*.log'
            }

        # Use the most recent debug file
        latest_debug = max(debug_files, key=lambda x: x.stat().st_mtime)
        reference_file = self.project_root / 'tests/reference/reports/cross_reference_validation_debug_reference.log'

        # Compare with reference (like vdiff alias)
        cmd = ['diff', str(reference_file), str(latest_debug)]
        exit_code, stdout, stderr = self._run_command(cmd)

        if exit_code == 0:
            return {'passed': True, 'details': 'PASS: No differences with reference log'}
        else:
            return {
                'passed': False,
                'error': 'Three-way validation regression detected',
                'details': f"Diff output:\n{stdout}"
            }

    def _run_ediff_test(self) -> Dict:
        """Run ediff test: Compare Excel report with reference"""
        self.log("Validating Excel report output...")

        # Find the generated report file
        report_files = list(self.project_root.glob('data/output/reports/BeAScout_Quality_Report_*.xlsx'))
        if not report_files:
            return {
                'passed': False,
                'error': 'No Excel report file found',
                'details': 'Expected files in data/output/reports/ matching pattern BeAScout_Quality_Report_*.xlsx'
            }

        # Use the most recent report file
        latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
        reference_report = self.project_root / 'tests/reference/reports/BeAScout_Quality_Report_anonymized.xlsx'

        # Use the Excel comparison tool (like ediff alias)
        comparison_tool = self.project_root / 'tests/tools/compare_excel_files.py'
        if not comparison_tool.exists():
            return {
                'passed': False,
                'error': 'Excel comparison tool not found',
                'details': f'Expected tool: {comparison_tool}'
            }

        cmd = [
            'python3', str(comparison_tool),
            str(reference_report),
            str(latest_report),
            '--exit-code',
            '--quiet'
        ]

        exit_code, stdout, stderr = self._run_command(cmd)

        if exit_code == 0:
            return {
                'passed': True,
                'details': 'PASS: Excel reports are functionally identical'
            }
        elif exit_code == 1:
            return {
                'passed': False,
                'error': 'Excel report regression detected',
                'details': f"Comparison output:\n{stdout}\n{stderr}"
            }
        else:
            return {
                'passed': False,
                'error': f'Excel comparison tool failed with exit code {exit_code}',
                'details': f"STDERR: {stderr}\nSTDOUT: {stdout}"
            }

    def _run_dudiff_test(self) -> Dict:
        """Run dudiff test: Discarded units regression test (currently disabled)"""
        return {
            'passed': False,
            'error': 'Test disabled due to known defect (issue #5)',
            'details': 'Town extraction regressions in discarded unit debug logs'
        }

    def run_test(self, test_name: str) -> Dict:
        """Run a specific regression test"""
        if test_name not in self.tests:
            return {
                'passed': False,
                'error': f'Unknown test: {test_name}',
                'details': f'Available tests: {list(self.tests.keys())}'
            }

        test_config = self.tests[test_name]

        if not test_config['enabled']:
            return {
                'passed': False,
                'error': f'Test {test_name} is disabled',
                'details': 'Check test configuration for reason'
            }

        self.log(f"Running {test_config['name']}...")

        try:
            return test_config['command']()
        except Exception as e:
            return {
                'passed': False,
                'error': f'Test execution failed with exception: {str(e)}',
                'details': f'Exception type: {type(e).__name__}'
            }

    def run_all_tests(self, step_filter: Optional[str] = None) -> Dict:
        """Run sequential pipeline with fail-fast regression testing"""
        self.log("Starting BeAScout Sequential Pipeline + Regression Tests...")
        self.log(f"Project root: {self.project_root}")
        self.log(f"Session ID: {self.session_manager.session_id}")

        # Setup logging for regression test runner
        regression_log_path = self.session_manager.get_log_path("run_regression_tests")
        self.log(f"📄 Regression test log: {regression_log_path}")

        # Check prerequisites
        if not self._check_prerequisites():
            return {
                'success': False,
                'error': 'Prerequisites not met',
                'results': []
            }

        # Determine which steps to run
        if step_filter:
            # For backwards compatibility with individual test names
            step_map = {
                'udiff': [1, 2],  # process_full_dataset + udiff
                'vdiff': [1, 2, 3, 4],  # process_full_dataset + udiff + three_way_validator + vdiff
                'ediff': [1, 2, 3, 4, 5, 6]  # all steps
            }
            if step_filter in step_map:
                steps_to_run = [i-1 for i in step_map[step_filter]]  # Convert to 0-based index
            else:
                return {
                    'success': False,
                    'error': f'Unknown step filter: {step_filter}',
                    'results': []
                }
        else:
            steps_to_run = list(range(len(self.pipeline_steps)))

        total_steps = len(steps_to_run)
        self.log(f"Running {total_steps} sequential steps with fail-fast behavior")

        # Run each step in sequence with fail-fast
        results = []
        overall_success = True

        for i, step_index in enumerate(steps_to_run):
            step = self.pipeline_steps[step_index]
            current_step = i + 1

            self.log(f"\n{'='*70}")
            self.log(f"STEP {current_step}/{total_steps}: {step['name']}")
            self.log(f"DESC: {step['description']}")
            self.log('='*70)

            try:
                result = step['command']()
                result['step_name'] = step['name']
                result['step_number'] = current_step
                result['total_steps'] = total_steps

                if result['passed']:
                    self.log(f"✅ STEP {current_step}/{total_steps} PASSED: {step['name']}", "SUCCESS")
                    if self.verbose and 'details' in result:
                        self.log(f"Details: {result['details']}")
                else:
                    self.log(f"❌ STEP {current_step}/{total_steps} FAILED: {step['name']}", "ERROR")
                    self.log(f"Error: {result['error']}", "ERROR")
                    if self.verbose and 'details' in result:
                        self.log(f"Details: {result['details']}")
                    overall_success = False
                    results.append(result)
                    break  # FAIL FAST - Stop on first failure

                results.append(result)

            except Exception as e:
                self.log(f"❌ STEP {current_step}/{total_steps} FAILED: {step['name']}", "ERROR")
                self.log(f"Exception: {str(e)}", "ERROR")
                overall_success = False
                results.append({
                    'passed': False,
                    'step_name': step['name'],
                    'step_number': current_step,
                    'total_steps': total_steps,
                    'error': f'Step execution failed with exception: {str(e)}',
                    'details': f'Exception type: {type(e).__name__}'
                })
                break  # FAIL FAST - Stop on first failure

        # Collect all generated files for final summary
        self._collect_generated_files()

        return {
            'success': overall_success,
            'results': results,
            'summary': self._generate_summary(results),
            'generated_files': sorted(self.generated_files),
            'session_id': self.session_manager.session_id,
            'log_files': self._get_session_log_files()
        }

    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate step summary statistics"""
        total_steps = len(results)
        passed_steps = sum(1 for r in results if r['passed'])
        failed_steps = total_steps - passed_steps

        return {
            'total_steps': total_steps,
            'passed_steps': passed_steps,
            'failed_steps': failed_steps,
            'pass_rate': round((passed_steps / total_steps) * 100, 1) if total_steps > 0 else 0
        }

    def _collect_generated_files(self):
        """Collect all files generated during this session (excluding log files)"""
        import time

        # Look for files with our session timestamp
        session_pattern = f"*{self.session_manager.session_id}*"

        # Check output directories (excluding debug which needs special handling)
        output_dirs = [
            self.project_root / "data/output/reports",
            self.project_root / "data/raw"
        ]

        for output_dir in output_dirs:
            if output_dir.exists():
                for file_path in output_dir.glob(session_pattern):
                    if file_path.is_file():
                        self.generated_files.append(str(file_path.relative_to(self.project_root)))

        # Special handling for debug files - they use their own timestamps, not session_id
        # Look for debug files created during our test run (after test start time)
        debug_dir = self.project_root / "data/debug"
        if debug_dir.exists() and hasattr(self, 'test_start_time'):
            debug_patterns = [
                "discarded_unit_identifier_debug_scraped_*.log",
                "unit_identifier_debug_scraped_*.log",
                "cross_reference_validation_debug_*.log"
            ]

            for pattern in debug_patterns:
                for debug_file in debug_dir.glob(pattern):
                    if debug_file.is_file() and debug_file.stat().st_mtime >= self.test_start_time:
                        self.generated_files.append(str(debug_file.relative_to(self.project_root)))

    def _get_session_log_files(self) -> List[str]:
        """Get actual log files for this session (not debug output files)"""
        log_files = []

        # Session log files from data/logs/
        scripts = ["run_regression_tests", "process_full_dataset", "three_way_validator", "generate_commissioner_report"]
        for script in scripts:
            log_path = self.session_manager.get_log_path(script)
            if log_path.exists():
                try:
                    log_files.append(str(log_path.relative_to(self.project_root)))
                except ValueError:
                    # Fallback: use absolute path if relative_to fails
                    log_files.append(str(log_path))

        return sorted(log_files)

    def _get_session_debug_files(self) -> List[str]:
        """Get debug output files for this session"""
        debug_files = []

        # Debug files from data/debug/ with session timestamp
        debug_dir = self.project_root / "data/debug"
        if debug_dir.exists():
            debug_patterns = [
                "discarded_unit_identifier_debug_scraped_*.log",
                "unit_identifier_debug_scraped_*.log",
                "cross_reference_validation_debug_*.log"
            ]

            for pattern in debug_patterns:
                # Find files that match both the pattern and contain our session timestamp
                for debug_file in debug_dir.glob(pattern):
                    if self.session_manager.session_id in debug_file.name:
                        try:
                            debug_files.append(str(debug_file.relative_to(self.project_root)))
                        except ValueError:
                            # Fallback: use absolute path if relative_to fails
                            debug_files.append(str(debug_file))

        return sorted(debug_files)

    def cleanup(self):
        """Clean up temporary files"""
        for temp_path in self.temp_dirs:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def main():
    """CLI interface for regression test runner"""
    parser = argparse.ArgumentParser(
        description="BeAScout Regression Test Runner",
        epilog="""
Examples:
  # Run all regression tests
  python tests/run_regression_tests.py

  # Run only udiff test
  python tests/run_regression_tests.py --test udiff

  # Run with detailed output
  python tests/run_regression_tests.py --verbose

  # Run specific test with exit code for automation
  python tests/run_regression_tests.py --test ediff --exit-code
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--test', choices=['udiff', 'vdiff', 'ediff', 'dudiff'],
                       help='Run specific test only')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Detailed output')
    parser.add_argument('--exit-code', action='store_true',
                       help='Exit with code 0 if all pass, 1 if any fail')

    # Add session management arguments (excluding conflicting --verbose)
    parser.add_argument('--session-id', type=str,
                      help='Session timestamp (YYYYMMDD_HHMMSS) for file correlation')
    parser.add_argument('--session-type', type=str, default='regression',
                      choices=['pipeline', 'regression', 'development'],
                      help='Type of pipeline session')
    parser.add_argument('--log', action='store_true',
                      help='Direct stdout/stderr to log file')

    args = parser.parse_args()

    # Create session manager from arguments
    session_manager = SessionManager(
        session_id=args.session_id,
        session_type=getattr(args, 'session_type', 'regression')
    )

    # Initialize test runner with session management
    runner = RegressionTestRunner(verbose=args.verbose)
    runner.session_manager = session_manager

    # Use session logging context manager - always log for regression tests with terse terminal
    with session_logging(session_manager, "run_regression_tests",
                        log_enabled=True, verbose=args.verbose, terminal_terse=True):
        try:
            # Run tests
            results = runner.run_all_tests(step_filter=args.test)

            # Display final summary on terminal and log file using log_and_terse_print
            session_manager.log_and_terse_print(f"\n{'='*80}")
            session_manager.log_and_terse_print("REGRESSION TEST SUMMARY")
            session_manager.log_and_terse_print('='*80)

            if not results.get('success', False):
                session_manager.log_and_terse_print("❌ SOME TESTS FAILED")
                if 'error' in results:
                    session_manager.log_and_terse_print(f"Error: {results['error']}")
            else:
                session_manager.log_and_terse_print("✅ ALL TESTS PASSED")

            if 'summary' in results:
                summary = results['summary']
                session_manager.log_and_terse_print(f"📊 Steps: {summary['passed_steps']}/{summary['total_steps']} passed ({summary['pass_rate']}%)")

            # Session information
            if 'session_id' in results:
                session_manager.log_and_terse_print(f"🔍 Session ID: {results['session_id']}")

            # Generated files
            if 'generated_files' in results and results['generated_files']:
                session_manager.log_and_terse_print(f"\n📁 Generated Files:")
                for file_path in sorted(results['generated_files']):
                    session_manager.log_and_terse_print(f"  - {file_path}")

            # Log files
            if 'log_files' in results and results['log_files']:
                session_manager.log_and_terse_print(f"\n📄 Log Files:")
                for log_file in results['log_files']:
                    session_manager.log_and_terse_print(f"  - {log_file}")

            # Detailed results
            if 'results' in results and args.verbose:
                session_manager.terse_print(f"\nDetailed Results:")
                for result in results['results']:
                    status = "✅ PASS" if result['passed'] else "❌ FAIL"
                    step_info = f"Step {result.get('step_number', '?')}/{result.get('total_steps', '?')}"
                    session_manager.terse_print(f"  {status} - {step_info}: {result['step_name']}")
                    if not result['passed']:
                        session_manager.terse_print(f"    Error: {result['error']}")

            # Exit with appropriate code
            if args.exit_code:
                sys.exit(0 if results['success'] else 1)

        except KeyboardInterrupt:
            session_manager.terse_print("\n⚠️  Tests interrupted by user")
            if args.exit_code:
                sys.exit(130)
        except Exception as e:
            session_manager.terse_print(f"❌ Regression test runner failed: {e}")
            if args.exit_code:
                sys.exit(2)
        finally:
            runner.cleanup()


if __name__ == "__main__":
    main()