#!/usr/bin/env python3
"""
BeAScout Weekly Quality Report Pipeline Manager
Orchestrates complete data pipeline from scraping to report generation
Designed for Sunday evening execution with robust error handling and recovery

Pipeline Stages:
1. Scraping: BeAScout + JoinExploring data for all HNE zip codes
2. Processing: Convert HTML to structured JSON with quality scoring
3. Key Three Conversion: Convert Excel to JSON format
4. Validation: Correlate with Key Three registry for completeness
5. Reporting: Generate Excel report for manual email distribution
6. Analytics: Generate weekly analytics and compare with previous week
7. Email Draft: Create complete email draft for copy/paste distribution
8. Unit Emails (Optional): Generate personalized improvement emails with timestamps
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class WarningErrorHandler(logging.Handler):
    """Custom log handler that captures warnings and errors"""

    def __init__(self, pipeline):
        super().__init__()
        self.pipeline = pipeline

    def emit(self, record):
        # Avoid infinite recursion - don't capture our own summary messages
        message = record.getMessage()

        # Skip summary section messages (prevents infinite loop when reporting warnings/errors)
        summary_indicators = [
            "PIPELINE COMPLETION SUMMARY",
            "📋 WARNINGS:",
            "❌ ERRORS:",
            "⚠️  ISSUES DETECTED:",
            "✅ No warnings or errors"
        ]

        # Skip numbered list items from summary (starts with spaces + number + dot)
        if any(indicator in message for indicator in summary_indicators):
            return
        if message.strip() and message[0:10].strip() and message.strip()[0].isdigit() and '. ' in message[:10]:
            return

        if record.levelno >= logging.ERROR:
            self.pipeline.errors.append(message)
        elif record.levelno >= logging.WARNING:
            self.pipeline.warnings.append(message)

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class PipelineStage:
    """Represents a single pipeline stage with status tracking"""

    def __init__(self, name: str, description: str, script_path: str = None,
                 required_files: List[str] = None, output_files: List[str] = None):
        self.name = name
        self.description = description
        self.script_path = script_path
        self.required_files = required_files or []
        self.output_files = output_files or []
        self.status = "pending"  # pending, running, completed, failed, skipped
        self.start_time = None
        self.end_time = None
        self.error_message = None

    def start(self):
        """Mark stage as running"""
        self.status = "running"
        self.start_time = datetime.now()

    def complete(self):
        """Mark stage as completed"""
        self.status = "completed"
        self.end_time = datetime.now()

    def fail(self, error_message: str):
        """Mark stage as failed with error"""
        self.status = "failed"
        self.end_time = datetime.now()
        self.error_message = error_message

    def skip(self, reason: str):
        """Mark stage as skipped"""
        self.status = "skipped"
        self.error_message = reason

    @property
    def duration(self) -> Optional[float]:
        """Get stage duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

class WeeklyReportPipeline:
    """
    Main pipeline manager for BeAScout weekly quality reports
    Handles orchestration, error recovery, and status tracking
    """

    def __init__(self, skip_failed_zips: bool = False, fallback_to_cache: bool = False, key_three_file: str = None, scraped_dir: str = None, baseline_file: str = None, generate_unit_emails: bool = False):
        """
        Initialize weekly report pipeline.

        Args:
            skip_failed_zips: Continue processing even if some zip codes fail during scraping
            fallback_to_cache: Use cached/existing data if fresh scraping fails
            key_three_file: Path to Key Three Excel file with unit registry
            scraped_dir: Path to EXISTING scraped session directory (input) - skips scraping stage
            baseline_file: Baseline analytics JSON file for week-over-week comparison
            generate_unit_emails: Generate personalized unit improvement emails with PDFs
        """
        self.skip_failed_zips = skip_failed_zips
        self.fallback_to_cache = fallback_to_cache
        self.key_three_file = key_three_file
        self.baseline_file = baseline_file
        self.generate_unit_emails = generate_unit_emails
        self.start_time = datetime.now()
        self.session_id = self.start_time.strftime("%Y%m%d_%H%M%S")

        # Session-specific data tracking
        self.scraped_session_dir = scraped_dir
        self.scraped_session_id = self._extract_scraped_session_id()

        # Warning and error tracking
        self.warnings = []
        self.errors = []

        # Setup logging
        self.setup_logging()

        # Define pipeline stages
        self.stages = self._define_pipeline_stages()

        # Status tracking
        self.status_file = project_root / "data" / "logs" / f"pipeline_status_{self.session_id}.json"

        self.logger.info(f"🚀 Weekly Report Pipeline initialized (Session: {self.session_id})")

    def setup_logging(self):
        """Configure logging with file and console output"""
        log_dir = project_root / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"generate_weekly_report_{self.session_id}.log"

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Warning/error tracking handler
        warning_error_handler = WarningErrorHandler(self)
        warning_error_handler.setLevel(logging.WARNING)

        # Configure logger
        self.logger = logging.getLogger('pipeline')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(warning_error_handler)

        self.logger.info(f"📝 Logging configured: {log_file}")

    def _report_completion_summary(self, overall_success: bool) -> bool:
        """Report completion summary with warnings and errors highlighted"""
        # Count issues
        warning_count = len(self.warnings)
        error_count = len(self.errors)

        # Determine final status
        has_issues = warning_count > 0 or error_count > 0
        final_success = overall_success and not has_issues

        # Always show summary header
        self.logger.info("=" * 80)
        self.logger.info("PIPELINE COMPLETION SUMMARY")
        self.logger.info("=" * 80)

        # Show issue counts
        if has_issues:
            self.logger.error(f"⚠️  ISSUES DETECTED: {warning_count} warnings, {error_count} errors")
        else:
            self.logger.info("✅ No warnings or errors detected")

        # Show all warnings
        if self.warnings:
            self.logger.warning("📋 WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                self.logger.warning(f"  {i}. {warning}")

        # Show all errors
        if self.errors:
            self.logger.error("❌ ERRORS:")
            for i, error in enumerate(self.errors, 1):
                self.logger.error(f"  {i}. {error}")

        # Final status
        if final_success:
            self.logger.info("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        else:
            if has_issues:
                self.logger.error("💥 PIPELINE COMPLETED WITH ISSUES - Review warnings/errors above")
            else:
                self.logger.error("💥 PIPELINE FAILED!")

        self.logger.info("=" * 80)
        return final_success

    def _define_pipeline_stages(self) -> Dict[str, PipelineStage]:
        """Define all pipeline stages with dependencies and validation"""
        return {
            "scraping": PipelineStage(
                name="scraping",
                description="Scrape BeAScout and JoinExploring data for all HNE zip codes",
                script_path="src/pipeline/acquisition/multi_zip_scraper.py",
                required_files=[
                    "data/zipcodes/hne_council_zipcodes.json"
                ],
                output_files=[
                    "data/scraped/*/session_summary.json",
                    "data/scraped/*/beascout_*.html",
                    "data/scraped/*/joinexploring_*.html"
                ]
            ),
            "processing": PipelineStage(
                name="processing",
                description="Process scraped HTML into structured unit data with quality scoring",
                script_path="src/pipeline/processing/process_full_dataset.py",
                required_files=[
                    "data/scraped/session_summary.json"
                ],
                output_files=[
                    "data/raw/all_units_comprehensive_scored.json"
                ]
            ),
            "key_three_conversion": PipelineStage(
                name="key_three_conversion",
                description="Convert Key Three Excel file to clean JSON format",
                script_path="src/dev/tools/convert_key_three_to_json.py",
                required_files=[
                    "data/input/Key*3*.xlsx"
                ],
                output_files=[
                    "data/input/Key_3_08-22-2025.json"
                ]
            ),
            "validation": PipelineStage(
                name="validation",
                description="Correlate scraped data with Key Three registry for completeness",
                script_path="src/pipeline/analysis/three_way_validator.py",
                required_files=[
                    "data/raw/all_units_comprehensive_scored.json",
                    "data/input/Key_3_08-22-2025.json"
                ],
                output_files=[
                    "data/output/enhanced_three_way_validation_results.json"
                ]
            ),
            "reporting": PipelineStage(
                name="reporting",
                description="Generate comprehensive Excel quality report for leadership distribution",
                script_path="src/pipeline/analysis/generate_commissioner_report.py",
                required_files=[
                    "data/raw/all_units_comprehensive_scored.json",
                    "data/output/enhanced_three_way_validation_results.json"
                ],
                output_files=[
                    "data/output/reports/weekly/BeAScout_Weekly_Quality_Report_*.xlsx"
                ]
            ),
            "analytics": PipelineStage(
                name="analytics",
                description="Generate weekly analytics and comparison with previous week",
                script_path="src/pipeline/analysis/generate_weekly_analytics.py",
                required_files=[
                    "data/output/reports/weekly/BeAScout_Weekly_Quality_Report_*.xlsx"
                ],
                output_files=[
                    "data/output/reports/weekly/BeAScout_Weekly_Quality_Report_*.json"
                ]
            ),
            "email_draft": PipelineStage(
                name="email_draft",
                description="Generate weekly email draft with statistics for manual distribution",
                script_path="src/pipeline/analysis/generate_weekly_email_draft.py",
                required_files=[
                    "data/output/reports/weekly/BeAScout_Weekly_Quality_Report_*.json",
                    "data/config/email_distribution.json"
                ],
                output_files=[
                    "data/output/reports/weekly/BeAScout_Weekly_Email_Draft_*.txt"
                ]
            ),
            "unit_emails": PipelineStage(
                name="unit_emails",
                description="Generate personalized unit improvement emails with council branding",
                script_path="src/pipeline/analysis/generate_unit_emails.py",
                required_files=[
                    "data/output/enhanced_three_way_validation_results.json"
                ],
                output_files=[
                    "data/output/unit_emails/*.md"
                ]
            ),
            "unit_email_pdfs": PipelineStage(
                name="unit_email_pdfs",
                description="Convert unit improvement emails to professional PDF format",
                script_path="src/pipeline/analysis/generate_unit_email_pdfs.py",
                required_files=[
                    "data/output/unit_emails/*.md"
                ],
                output_files=[
                    "data/output/unit_emails/*.pdf"
                ]
            )
        }

    def pre_flight_checks(self) -> bool:
        """Run comprehensive pre-flight checks before starting pipeline"""
        self.logger.info("🔍 Running pre-flight checks...")

        checks_passed = True

        # Check disk space (need at least 1GB free)
        try:
            import shutil
            free_space = shutil.disk_usage(project_root).free / (1024**3)  # GB
            if free_space < 1.0:
                self.logger.error(f"❌ Insufficient disk space: {free_space:.1f}GB free (need 1GB+)")
                checks_passed = False
            else:
                self.logger.info(f"✅ Disk space OK: {free_space:.1f}GB free")
        except Exception as e:
            self.logger.warning(f"⚠️  Could not check disk space: {e}")

        # Check required directories exist
        required_dirs = [
            "data/input",
            "data/scraped",
            "data/raw",
            "data/output/reports/weekly",
            "data/logs",
            "data/config"
        ]

        for dir_path in required_dirs:
            full_path = project_root / dir_path
            if not full_path.exists():
                self.logger.info(f"📁 Creating directory: {dir_path}")
                full_path.mkdir(parents=True, exist_ok=True)
            else:
                self.logger.debug(f"✅ Directory exists: {dir_path}")

        # Check for Key Three data
        if self.key_three_file:
            # Use specified file
            key_three_path = project_root / self.key_three_file
            if key_three_path.exists():
                self.logger.info(f"✅ Key Three data found (specified): {key_three_path.name}")
            else:
                self.logger.error(f"❌ Specified Key Three file not found: {self.key_three_file}")
                checks_passed = False
        else:
            # Auto-detect Key Three files (prioritize Excel with spaces, then CSV)
            key_three_excel_spaces = list((project_root / "data" / "input").glob("Key 3 *.xlsx"))
            key_three_excel_underscores = list((project_root / "data" / "input").glob("Key_3_*.xlsx"))
            key_three_csv = list((project_root / "data" / "input").glob("Key_3_*.csv"))

            # Prioritize Excel files with spaces, then underscores, then CSV
            key_three_files = key_three_excel_spaces + key_three_excel_underscores + key_three_csv

            if not key_three_files:
                self.logger.error("❌ No Key Three files found in data/input/")
                self.logger.error("   Expected: data/input/Key 3 *.xlsx or data/input/Key_3_*.csv")
                self.logger.error("   Or use --key-three-file to specify exact file")
                checks_passed = False
            else:
                # Use first file from prioritized list (Excel with spaces gets priority)
                preferred_key_three = key_three_files[0]
                self.logger.info(f"✅ Key Three data found (auto-detected): {preferred_key_three.name}")

        # Check network connectivity (test actual search endpoints)
        try:
            import urllib.request
            # Test BeAScout search endpoint (more representative than homepage)
            test_url = "https://beascout.scouting.org/list/?zip=01720&program[0]=pack&miles=10"
            urllib.request.urlopen(test_url, timeout=10)
            self.logger.info("✅ Network connectivity OK")
        except Exception as e:
            # If search endpoint fails, try basic connectivity
            try:
                import socket
                socket.create_connection(("beascout.scouting.org", 443), timeout=10).close()
                self.logger.info("✅ Network connectivity OK (basic check)")
            except Exception as e2:
                self.logger.error(f"❌ Network connectivity failed: {e}")
                if not self.fallback_to_cache:
                    checks_passed = False
                else:
                    self.logger.warning("⚠️  Will attempt to use cached data if available")

        # Check Python dependencies
        required_modules = {
            'playwright': 'playwright',
            'pandas': 'pandas',
            'openpyxl': 'openpyxl',
            'beautifulsoup4': 'bs4'  # beautifulsoup4 imports as 'bs4'
        }
        for display_name, import_name in required_modules.items():
            try:
                __import__(import_name)
                self.logger.debug(f"✅ Module available: {display_name}")
            except ImportError:
                self.logger.error(f"❌ Missing required module: {display_name}")
                checks_passed = False

        if checks_passed:
            self.logger.info("✅ All pre-flight checks passed")
        else:
            self.logger.error("❌ Pre-flight checks failed - cannot proceed")

        return checks_passed

    def validate_stage_requirements(self, stage: PipelineStage) -> bool:
        """Check if stage requirements are met"""
        self.logger.debug(f"🔍 Validating requirements for stage: {stage.name}")

        # Special handling for processing stage - use scraped directory
        if stage.name == "processing" and self.scraped_session_dir:
            # Check for session summary in the specified scraped directory
            session_summary = Path(self.scraped_session_dir) / "session_summary.json"
            if not session_summary.exists():
                self.logger.error(f"❌ Session summary missing in scraped directory: {session_summary}")
                return False
            else:
                self.logger.debug(f"✅ Session summary found: {session_summary}")
                return True

        # Standard requirements validation for other stages
        for req_file_pattern in stage.required_files:
            # Handle glob patterns
            if '*' in req_file_pattern:
                matches = list(project_root.glob(req_file_pattern))
                if not matches:
                    self.logger.error(f"❌ Required file pattern not found: {req_file_pattern}")
                    return False
                else:
                    self.logger.debug(f"✅ Found {len(matches)} files matching: {req_file_pattern}")
            else:
                req_file = project_root / req_file_pattern
                if not req_file.exists():
                    self.logger.error(f"❌ Required file missing: {req_file_pattern}")
                    return False
                else:
                    self.logger.debug(f"✅ Required file exists: {req_file_pattern}")

        return True

    def validate_stage_outputs(self, stage: PipelineStage) -> bool:
        """Check if stage produced expected outputs"""
        self.logger.debug(f"🔍 Validating outputs for stage: {stage.name}")

        outputs_found = []
        for output_pattern in stage.output_files:
            if '*' in output_pattern:
                matches = list(project_root.glob(output_pattern))
                if matches:
                    outputs_found.extend(matches)
                    self.logger.debug(f"✅ Found {len(matches)} output files: {output_pattern}")
                else:
                    self.logger.error(f"❌ No output files found: {output_pattern}")
                    return False
            else:
                output_file = project_root / output_pattern
                if output_file.exists():
                    outputs_found.append(output_file)
                    self.logger.debug(f"✅ Output file exists: {output_pattern}")
                else:
                    self.logger.error(f"❌ Expected output file missing: {output_pattern}")
                    return False

        # Additional validation for specific stages
        if stage.name == "scraping":
            return self._validate_scraping_outputs(outputs_found)
        elif stage.name == "processing":
            return self._validate_processing_outputs(outputs_found)
        elif stage.name == "validation":
            return self._validate_validation_outputs(outputs_found)
        elif stage.name == "reporting":
            return self._validate_reporting_outputs(outputs_found)

        return True

    def _validate_scraping_outputs(self, output_files: List[Path]) -> bool:
        """Validate scraping stage outputs"""
        session_summary = None
        scraped_files = []

        # PRIORITY: Look for session_summary.json in current session directory FIRST
        current_session_dir = Path(f"data/scraped/{self.session_id}")
        current_session_summary = current_session_dir / "session_summary.json"

        if current_session_summary.exists():
            session_summary = current_session_summary
            self.scraped_session_dir = str(current_session_dir)
            self.logger.info(f"✅ Using current session directory: {self.scraped_session_dir}")

            # Collect HTML files from current session directory
            scraped_files = list(current_session_dir.glob("*.html"))
        else:
            # Fallback: Look through output_files (old logic for compatibility)
            self.logger.warning(f"⚠️  Current session directory not found: {current_session_dir}")
            self.logger.info("🔍 Searching through output files for session data...")

            for file_path in output_files:
                if file_path.name == "session_summary.json":
                    session_summary = file_path
                    self.scraped_session_dir = str(file_path.parent)
                    self.logger.warning(f"⚠️  Using fallback session directory: {self.scraped_session_dir}")
                    break

            # Collect HTML files from fallback directory
            for file_path in output_files:
                if file_path.name.endswith('.html'):
                    scraped_files.append(file_path)

        if not session_summary:
            self.logger.error("❌ Session summary file missing")
            return False

        try:
            with open(session_summary) as f:
                summary_data = json.load(f)

            zip_count = summary_data.get('total_zip_codes', 0)
            if zip_count < 70:  # Expect ~71 HNE zip codes
                self.logger.warning(f"⚠️  Only scraped {zip_count} zip codes (expected ~71)")
                if not self.skip_failed_zips:
                    return False

            self.logger.info(f"✅ Scraping validation passed: {zip_count} zip codes, {len(scraped_files)} data files")
            self.logger.info(f"📁 Session directory captured: {self.scraped_session_dir}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Error validating scraping outputs: {e}")
            return False

    def _validate_processing_outputs(self, output_files: List[Path]) -> bool:
        """Validate processing stage outputs"""
        try:
            for file_path in output_files:
                if 'comprehensive_scored' in file_path.name:
                    with open(file_path) as f:
                        data = json.load(f)

                    units = data.get('scraped_units', data.get('units_with_scores', []))
                    if len(units) < 150:  # Expect ~165 HNE units
                        self.logger.warning(f"⚠️  Only processed {len(units)} units (expected ~165)")

                    # Check for quality scoring
                    scored_units = [u for u in units if 'completeness_score' in u]
                    if len(scored_units) != len(units):
                        self.logger.error(f"❌ Quality scoring incomplete: {len(scored_units)}/{len(units)} units scored")
                        return False

                    self.logger.info(f"✅ Processing validation passed: {len(units)} units with quality scores")
                    return True

            self.logger.error("❌ No comprehensive scored data file found")
            return False

        except Exception as e:
            self.logger.error(f"❌ Error validating processing outputs: {e}")
            return False

    def _validate_validation_outputs(self, output_files: List[Path]) -> bool:
        """Validate validation stage outputs"""
        try:
            for file_path in output_files:
                if 'validation_results' in file_path.name:
                    with open(file_path) as f:
                        data = json.load(f)

                    results = data.get('validation_results', [])
                    summary = data.get('validation_summary', {})

                    correlation_rate = summary.get('validation_percentages', {}).get('both_sources', 0)
                    if correlation_rate < 95:  # Expect high correlation
                        self.logger.warning(f"⚠️  Low correlation rate: {correlation_rate}%")

                    self.logger.info(f"✅ Validation passed: {len(results)} units analyzed, {correlation_rate}% correlation")
                    return True

            self.logger.error("❌ No validation results file found")
            return False

        except Exception as e:
            self.logger.error(f"❌ Error validating validation outputs: {e}")
            return False

    def _validate_reporting_outputs(self, output_files: List[Path]) -> bool:
        """Validate reporting stage outputs"""
        excel_files = [f for f in output_files if f.suffix == '.xlsx']

        if not excel_files:
            self.logger.error("❌ No Excel report files generated")
            return False

        # Check file size (should be substantial with real data)
        latest_report = max(excel_files, key=lambda p: p.stat().st_mtime)
        file_size_kb = latest_report.stat().st_size / 1024

        if file_size_kb < 10:  # Less than 10KB suggests empty/corrupt file
            self.logger.error(f"❌ Report file too small: {file_size_kb:.1f}KB")
            return False

        self.logger.info(f"✅ Reporting validation passed: {latest_report.name} ({file_size_kb:.1f}KB)")
        return True

    def run_stage(self, stage_name: str) -> bool:
        """Execute a single pipeline stage"""
        stage = self.stages[stage_name]

        self.logger.info(f"🚀 Starting stage: {stage.name}")
        self.logger.info(f"📝 Description: {stage.description}")

        stage.start()
        self.save_status()

        # Validate requirements
        if not self.validate_stage_requirements(stage):
            stage.fail("Requirements validation failed")
            self.save_status()
            return False

        # Pre-stage cleanup for unit_emails - remove old artifacts before generating new ones
        if stage.name == "unit_emails":
            email_dir = Path("data/output/unit_emails")
            if email_dir.exists():
                old_md_files = list(email_dir.glob("*.md"))
                old_pdf_files = list(email_dir.glob("*.pdf"))
                if old_md_files or old_pdf_files:
                    self.logger.info(f"🗑️  Cleaning up {len(old_md_files)} old .md and {len(old_pdf_files)} old .pdf files from prior runs")
                    for f in old_md_files + old_pdf_files:
                        f.unlink()

        # Execute stage
        success = self._execute_stage_script(stage)

        if success:
            # Validate outputs
            if self.validate_stage_outputs(stage):
                # Run regression testing BEFORE marking scraping stage complete
                if stage.name == "scraping":
                    try:
                        # Update scraped session directory to current session after successful scraping
                        current_session_dir = f"data/scraped/{self.session_id}"
                        if Path(current_session_dir).exists():
                            self.scraped_session_dir = current_session_dir
                            self.logger.info(f"✅ Updated scraped session directory to current session: {current_session_dir}")
                        else:
                            self.logger.warning(f"⚠️  Current session directory not found after scraping: {current_session_dir}")

                        self._run_udiff_regression_test()
                    except RuntimeError as e:
                        # Regression test failed - mark stage as failed
                        stage.fail(f"Regression test failed: {e}")
                        success = False
                        self.save_status()
                        return success

                # Mark stage complete only after regression test passes (for scraping) or if not scraping stage
                stage.complete()
                duration = stage.duration
                self.logger.info(f"✅ Stage completed: {stage.name} ({duration:.1f}s)")
            else:
                stage.fail("Output validation failed")
                success = False

        self.save_status()
        return success

    def _execute_stage_script(self, stage: PipelineStage) -> bool:
        """Execute the script for a pipeline stage"""
        if not stage.script_path:
            self.logger.error(f"❌ No script defined for stage: {stage.name}")
            return False

        script_file = project_root / stage.script_path
        if not script_file.exists():
            stage.fail(f"Script not found: {stage.script_path}")
            return False

        # Build command with appropriate arguments
        cmd_args = self._build_stage_command(stage)

        try:
            import subprocess

            self.logger.info(f"🔧 Executing: {sys.executable} {' '.join(cmd_args)}")

            # Run with real-time output (use -u flag for unbuffered output like in OPERATIONAL_WORKFLOW.md)
            process = subprocess.Popen(
                [sys.executable, '-u'] + cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,  # Line buffered
                cwd=project_root
            )

            # Stream output to log in real-time
            for line in iter(process.stdout.readline, ''):
                line = line.rstrip()
                if line:
                    self.logger.info(f"  {line}")

            return_code = process.wait()

            if return_code == 0:
                return True
            else:
                stage.fail(f"Script exited with code {return_code}")
                return False

        except Exception as e:
            stage.fail(f"Execution error: {e}")
            return False

    def _build_stage_command(self, stage: PipelineStage) -> List[str]:
        """Build command line arguments for stage script"""
        cmd_args = [stage.script_path]

        # Add stage-specific arguments
        if stage.name == "scraping":
            cmd_args.append("full")  # Run full scraping by default
            # Pass session ID to ensure scraped directory matches pipeline session
            cmd_args.extend(["--session-id", self.session_id])
            if self.skip_failed_zips:
                cmd_args.append("--skip-failed")
            if self.fallback_to_cache:
                cmd_args.append("--fallback-cache")

        elif stage.name == "processing":
            if self.scraped_session_dir:
                # Use explicitly set scraped directory (from resume or manual specification)
                cmd_args.append(self.scraped_session_dir)
            else:
                # Use current session ID to construct scraped directory path
                session_scraped_dir = f"data/scraped/{self.session_id}"
                if Path(session_scraped_dir).exists():
                    cmd_args.append(session_scraped_dir)
                    self.scraped_session_dir = session_scraped_dir
                    self.logger.info(f"✅ Using current session scraped directory: {session_scraped_dir}")
                else:
                    # Fall back to finding most recent session directory as last resort
                    self.logger.warning(f"⚠️  Current session directory not found: {session_scraped_dir}")
                    latest_session = self._find_latest_scraped_session()
                    if latest_session:
                        cmd_args.append(str(latest_session))
                        self.scraped_session_dir = str(latest_session)
                        self.logger.warning(f"⚠️  Using fallback session directory: {latest_session}")
                    else:
                        raise ValueError("No scraped session directory available for processing")

        elif stage.name == "key_three_conversion":
            if self.key_three_file:
                cmd_args.append(self.key_three_file)
            else:
                raise ValueError("Key Three file required for conversion stage")

        elif stage.name == "validation":
            # Use converted JSON file for validation (more reliable than Excel)
            json_key_three = self.key_three_file.replace('.xlsx', '.json').replace('.csv', '.json')
            cmd_args.extend(["--key-three", json_key_three])

        elif stage.name == "reporting":
            # Weekly pipeline mode - generate weekly report format
            cmd_args.extend(["--session-id", self.session_id])
            cmd_args.append("--weekly")
            # Pass Key Three file for accurate filename display
            if self.key_three_file:
                cmd_args.extend(["--key-three", self.key_three_file])
            # Pass scraped session ID if available for accurate timestamps
            if self.scraped_session_id:
                cmd_args.extend(["--scraped-session", self.scraped_session_id])

        elif stage.name == "analytics":
            # Add baseline parameter if specified
            if hasattr(self, 'baseline_file') and self.baseline_file:
                cmd_args.extend(["--baseline", self.baseline_file])

        elif stage.name == "email_draft":
            # Pass scraped session ID if available for accurate timestamps
            if self.scraped_session_id:
                cmd_args.extend(["--scraped-session", self.scraped_session_id])

        elif stage.name == "unit_emails":
            # Add validation results file as positional argument
            # (Key Three data is already joined in validation results - no need to pass separately)
            validation_file = "data/output/enhanced_three_way_validation_results.json"
            cmd_args.append(validation_file)

            # Pass timestamps for footer
            cmd_args.extend(["--analysis-timestamp", self.session_id])

            if self.scraped_session_id:
                cmd_args.extend(["--scraped-timestamp", self.scraped_session_id])

            # Extract Key Three timestamp from file modification time
            key_three_timestamp = self._get_key_three_timestamp()
            if key_three_timestamp:
                cmd_args.extend(["--key-three-timestamp", key_three_timestamp])

        return cmd_args

    def _extract_scraped_session_id(self) -> Optional[str]:
        """Extract session ID from scraped directory path"""
        if not self.scraped_session_dir:
            return None

        # Extract timestamp from path like "data/scraped/20250920_124820"
        session_path = Path(self.scraped_session_dir)
        if session_path.exists():
            return session_path.name
        return None

    def _get_key_three_timestamp(self) -> Optional[str]:
        """Extract date from Key Three filename (format: Key_3_MM-DD-YYYY.xlsx) - returns YYYYMMDD only"""
        if not self.key_three_file:
            return None

        key_three_path = project_root / self.key_three_file
        if not key_three_path.exists():
            return None

        try:
            # Extract date from filename pattern: Key_3_09-29-2025.xlsx or Key 3 09-29-2025.xlsx
            filename = key_three_path.stem  # Get filename without extension

            # Pattern: Key_3_MM-DD-YYYY or Key 3 MM-DD-YYYY
            import re
            match = re.search(r'(\d{2})-(\d{2})-(\d{4})', filename)

            if match:
                month, day, year = match.groups()
                # Convert to YYYYMMDD format (date only, no time)
                timestamp = f"{year}{month}{day}"
                self.logger.debug(f"✅ Extracted Key Three date from filename: {month}-{day}-{year}")
                return timestamp
            else:
                # Fallback to file modification date if pattern not found
                mtime = key_three_path.stat().st_mtime
                timestamp = datetime.fromtimestamp(mtime).strftime("%Y%m%d")
                self.logger.warning(f"⚠️  Could not extract date from Key Three filename pattern, using file mtime")
                return timestamp

        except Exception as e:
            self.logger.warning(f"⚠️  Could not extract Key Three date: {e}")
            return None

    def _find_latest_scraped_session(self) -> Optional[Path]:
        """Find the most recent scraped session directory"""
        scraped_dir = project_root / "data" / "scraped"
        if not scraped_dir.exists():
            return None

        # Find directories with session_summary.json
        session_dirs = []
        for item in scraped_dir.iterdir():
            if item.is_dir():
                session_summary = item / "session_summary.json"
                if session_summary.exists():
                    session_dirs.append(item)

        if not session_dirs:
            return None

        # Return most recent by modification time
        latest = max(session_dirs, key=lambda p: p.stat().st_mtime)
        self.logger.info(f"📁 Found latest scraped session: {latest.name}")
        return latest

    def _run_udiff_regression_test(self):
        """Compare scraped units with reference baseline using Python set comparison - raises exception on failure"""
        try:
            self.logger.info("🔍 Running regression test: comparing scraped units with reference baseline...")

            # Define reference file path
            reference_file = project_root / "tests" / "reference" / "units" / "unit_identifier_debug_scraped_reference_u.log"

            if not reference_file.exists():
                self.logger.warning(f"⚠️  REGRESSION TEST SKIPPED: Reference file not found: {reference_file}")
                return

            # Find latest debug file
            debug_dir = project_root / "data" / "debug"
            debug_pattern = "unit_identifier_debug_scraped_*.log"
            debug_files = list(debug_dir.glob(debug_pattern))

            if not debug_files:
                self.logger.warning(f"⚠️  REGRESSION TEST SKIPPED: No debug files found matching {debug_pattern}")
                return

            latest_debug = max(debug_files, key=lambda p: p.stat().st_mtime)
            self.logger.info(f"📋 Comparing: {latest_debug.name}")

            # Load reference units as set (deduplicated and sorted)
            with open(reference_file, 'r', encoding='utf-8') as f:
                reference_units = set(line.strip() for line in f if line.strip())

            # Load scraped units as set (deduplicated and sorted)
            with open(latest_debug, 'r', encoding='utf-8') as f:
                scraped_units = set(line.strip() for line in f if line.strip())

            # Compare sets
            added_units = scraped_units - reference_units
            removed_units = reference_units - scraped_units

            # Report results
            if added_units or removed_units:
                self.logger.error("❌ REGRESSION TEST FAILED: Unit changes detected")
                self.logger.error(f"   Reference: {len(reference_units)} units")
                self.logger.error(f"   Scraped:   {len(scraped_units)} units")

                if added_units:
                    self.logger.error(f"   ✨ {len(added_units)} units ADDED (showing first 10):")
                    for unit in sorted(added_units)[:10]:
                        self.logger.error(f"      + {unit}")
                    if len(added_units) > 10:
                        self.logger.error(f"      ... and {len(added_units) - 10} more")

                if removed_units:
                    self.logger.error(f"   ❌ {len(removed_units)} units REMOVED (showing first 10):")
                    for unit in sorted(removed_units)[:10]:
                        self.logger.error(f"      - {unit}")
                    if len(removed_units) > 10:
                        self.logger.error(f"      ... and {len(removed_units) - 10} more")

                raise RuntimeError(f"Regression test failed: {len(added_units)} units added, {len(removed_units)} units removed. Review changes before continuing.")
            else:
                self.logger.info(f"✅ REGRESSION TEST PASSED: {len(scraped_units)} units match reference baseline")

        except RuntimeError:
            # Re-raise RuntimeError (our own exceptions from above)
            raise
        except Exception as e:
            self.logger.error(f"❌ REGRESSION TEST ERROR: {e}")
            raise RuntimeError(f"Regression test error: {e}") from e

    def save_status(self):
        """Save current pipeline status to file"""
        status_data = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "last_update": datetime.now().isoformat(),
            "scraped_session_dir": self.scraped_session_dir,
            "stages": {}
        }

        for name, stage in self.stages.items():
            status_data["stages"][name] = {
                "status": stage.status,
                "start_time": stage.start_time.isoformat() if stage.start_time else None,
                "end_time": stage.end_time.isoformat() if stage.end_time else None,
                "duration": stage.duration,
                "error_message": stage.error_message
            }

        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"⚠️  Could not save status: {e}")

    def load_status(self, session_id: str = None) -> bool:
        """Load pipeline status from previous session"""
        if session_id:
            status_file = project_root / "data" / "logs" / f"pipeline_status_{session_id}.json"
        else:
            # Find most recent status file
            status_files = list((project_root / "data" / "logs").glob("pipeline_status_*.json"))
            if not status_files:
                return False
            status_file = max(status_files, key=lambda p: p.stat().st_mtime)

        if not status_file.exists():
            return False

        try:
            with open(status_file) as f:
                status_data = json.load(f)

            # Restore scraped session directory
            self.scraped_session_dir = status_data.get("scraped_session_dir")

            # Restore stage statuses
            for name, stage_data in status_data.get("stages", {}).items():
                if name in self.stages:
                    stage = self.stages[name]
                    stage.status = stage_data.get("status", "pending")
                    stage.error_message = stage_data.get("error_message")

                    if stage_data.get("start_time"):
                        stage.start_time = datetime.fromisoformat(stage_data["start_time"])
                    if stage_data.get("end_time"):
                        stage.end_time = datetime.fromisoformat(stage_data["end_time"])

            self.logger.info(f"📂 Loaded status from: {status_file.name}")
            return True

        except Exception as e:
            self.logger.warning(f"⚠️  Could not load status: {e}")
            return False

    def run_pipeline(self, stages_to_run: List[str] = None, resume: bool = False) -> bool:
        """Run the complete pipeline or specified stages"""
        if resume:
            if not self.load_status():
                self.logger.warning("⚠️  No previous session found, starting fresh")
                resume = False

        if not self.pre_flight_checks():
            self.logger.error("❌ Pre-flight checks failed - aborting")
            return False

        # Determine which stages to run
        if stages_to_run is None:
            stages_to_run = list(self.stages.keys())
            # Conditionally exclude unit email stages unless explicitly requested
            if not self.generate_unit_emails:
                if "unit_emails" in stages_to_run:
                    stages_to_run = [stage for stage in stages_to_run if stage != "unit_emails"]
                if "unit_email_pdfs" in stages_to_run:
                    stages_to_run = [stage for stage in stages_to_run if stage != "unit_email_pdfs"]

        # Skip scraping stage if scraped directory is provided
        if self.scraped_session_dir and "scraping" in stages_to_run:
            self.logger.info(f"✅ Scraped directory provided: {self.scraped_session_dir}")
            self.logger.info("⏭️  Skipping scraping stage - using existing data")
            stages_to_run = [stage for stage in stages_to_run if stage != "scraping"]
            # Mark scraping as completed
            self.stages["scraping"].status = "completed"

        # Filter stages if resuming
        if resume:
            # Skip completed stages
            remaining_stages = []
            for stage_name in stages_to_run:
                if self.stages[stage_name].status != "completed":
                    remaining_stages.append(stage_name)
            stages_to_run = remaining_stages

            if not stages_to_run:
                self.logger.info("✅ All stages already completed")
                return True

            self.logger.info(f"🔄 Resuming from stages: {', '.join(stages_to_run)}")

        # Execute stages
        overall_success = True
        for stage_name in stages_to_run:
            if stage_name not in self.stages:
                self.logger.error(f"❌ Unknown stage: {stage_name}")
                overall_success = False
                continue

            success = self.run_stage(stage_name)
            if not success:
                self.logger.error(f"❌ Stage failed: {stage_name}")
                overall_success = False
                break

        # Generate summary
        self.generate_summary()

        return overall_success

    def generate_summary(self):
        """Generate and display pipeline execution summary"""
        total_duration = (datetime.now() - self.start_time).total_seconds()

        self.logger.info("=" * 60)
        self.logger.info("📊 PIPELINE EXECUTION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Session ID: {self.session_id}")
        self.logger.info(f"Total Duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")

        # Stage summary
        for name, stage in self.stages.items():
            status_icon = {
                "completed": "✅",
                "failed": "❌",
                "running": "🔄",
                "skipped": "⏭️",
                "pending": "⏳"
            }.get(stage.status, "❓")

            duration_str = f"({stage.duration:.1f}s)" if stage.duration else ""
            self.logger.info(f"{status_icon} {name.capitalize()}: {stage.status} {duration_str}")

            if stage.error_message:
                self.logger.info(f"    Error: {stage.error_message}")

        # Output files summary
        self.logger.info("\n📁 OUTPUT FILES:")

        # Find latest report file
        report_files = list((project_root / "data" / "output" / "reports" / "weekly").glob("BeAScout_Weekly_Quality_Report_*.xlsx"))
        if report_files:
            latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
            file_size_mb = latest_report.stat().st_size / (1024 * 1024)
            self.logger.info(f"📋 Quality Report: {latest_report.name} ({file_size_mb:.1f}MB)")
            self.logger.info(f"    Location: {latest_report}")

        # Find latest analytics file
        analytics_files = list((project_root / "data" / "output" / "reports" / "weekly").glob("BeAScout_Weekly_Quality_Report_*.json"))
        if analytics_files:
            latest_analytics = max(analytics_files, key=lambda p: p.stat().st_mtime)
            self.logger.info(f"📊 Analytics Data: {latest_analytics.name}")

        # Find latest email draft
        email_files = list((project_root / "data" / "output" / "reports" / "weekly").glob("BeAScout_Weekly_Email_Draft_*.txt"))
        if email_files:
            latest_email = max(email_files, key=lambda p: p.stat().st_mtime)
            self.logger.info(f"📧 Email Draft: {latest_email.name}")
            self.logger.info(f"    Location: {latest_email}")

        # Distribution instructions
        if any(stage.status == "completed" for stage in self.stages.values()):
            self.logger.info("\n📧 MANUAL DISTRIBUTION INSTRUCTIONS:")
            self.logger.info("1. Open the latest BeAScout Weekly Email Draft (.txt file)")
            self.logger.info("2. Copy/paste recipients from 'EMAIL RECIPIENTS' section")
            self.logger.info("3. Copy/paste subject from 'EMAIL SUBJECT' section")
            self.logger.info("4. Copy/paste body from 'EMAIL BODY' section")
            self.logger.info("5. Attach the Excel file listed in 'ATTACHMENT' section")
            self.logger.info("6. Review and send email")
            if email_files:
                self.logger.info(f"\n📄 Email draft ready: {latest_email}")

        self.logger.info("=" * 60)

def main():
    """Main CLI interface for weekly report pipeline"""
    parser = argparse.ArgumentParser(
        description="BeAScout Weekly Quality Report Pipeline Manager",
        epilog="""
Examples:
  # Run complete pipeline
  python generate_weekly_report.py

  # Run complete pipeline with unit emails
  python generate_weekly_report.py --generate-unit-emails

  # Run specific stage only
  python generate_weekly_report.py --stage scraping
  python generate_weekly_report.py --stage reporting
  python generate_weekly_report.py --stage unit_emails

  # Resume from last failure
  python generate_weekly_report.py --resume

  # Skip failed zip codes and continue
  python generate_weekly_report.py --skip-failed-zips

  # Use cached data if fresh scraping fails
  python generate_weekly_report.py --fallback-to-cache

This pipeline orchestrates the complete data flow:
1. Scraping: BeAScout + JoinExploring data for all HNE zip codes
2. Processing: Convert HTML to structured JSON with quality scoring
3. Key Three Conversion: Convert Excel to JSON format
4. Validation: Correlate with Key Three registry for completeness
5. Reporting: Generate Excel report for manual email distribution
6. Analytics: Generate weekly analytics and compare with previous week
7. Email Draft: Create complete email draft for copy/paste distribution
8. Unit Emails (Optional): Generate personalized improvement emails with timestamps
   - Includes BeAScout scraping timestamp, Key Three report timestamp, and analysis timestamp
   - Review IDs use analysis timestamp for consistent session tracking
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--stage', choices=['scraping', 'processing', 'validation', 'reporting', 'analytics', 'email_draft', 'unit_emails', 'all'],
                       default='all', help='Pipeline stage to run [default: all]')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from last successful stage in previous session')
    parser.add_argument('--skip-failed-zips', action='store_true',
                       help='Skip zip codes that fail during scraping and continue')
    parser.add_argument('--fallback-to-cache', action='store_true',
                       help='Use cached data if fresh scraping fails')
    parser.add_argument('--session-id', help='Resume specific session ID')
    parser.add_argument('--key-three-file', help='Path to Key Three file (e.g., "data/input/Key 3 08-22-2025.xlsx")')
    parser.add_argument('--scraped-dir', help='Path to EXISTING scraped session directory to use instead of fresh scraping (e.g., "data/scraped/20250919_191632")')
    parser.add_argument('--baseline', help='Baseline analytics file for week-over-week comparison (e.g., "BeAScout_Weekly_Quality_Report_20250904_154530.json")')
    parser.add_argument('--generate-unit-emails', action='store_true',
                       help='Generate personalized unit improvement emails with council branding (adds unit_emails stage to pipeline)')

    args = parser.parse_args()

    # Create pipeline manager
    pipeline = WeeklyReportPipeline(
        skip_failed_zips=args.skip_failed_zips,
        fallback_to_cache=args.fallback_to_cache,
        key_three_file=args.key_three_file,
        scraped_dir=args.scraped_dir,
        baseline_file=args.baseline,
        generate_unit_emails=args.generate_unit_emails
    )

    # Log command-line arguments
    pipeline.logger.info("📝 Command-line arguments:")
    pipeline.logger.info(f"  --stage: {args.stage}")
    if args.resume:
        pipeline.logger.info(f"  --resume: {args.resume}")
    if args.skip_failed_zips:
        pipeline.logger.info(f"  --skip-failed-zips: {args.skip_failed_zips}")
    if args.fallback_to_cache:
        pipeline.logger.info(f"  --fallback-to-cache: {args.fallback_to_cache}")
    if args.session_id:
        pipeline.logger.info(f"  --session-id: {args.session_id}")
    if args.key_three_file:
        pipeline.logger.info(f"  --key-three: {args.key_three_file}")
    if args.scraped_dir:
        pipeline.logger.info(f"  --scraped-dir: {args.scraped_dir}")
    if args.baseline:
        pipeline.logger.info(f"  --baseline: {args.baseline}")
    if args.generate_unit_emails:
        pipeline.logger.info(f"  --generate-unit-emails: {args.generate_unit_emails}")

    # Determine stages to run
    if args.stage == 'all':
        stages_to_run = None  # Run all stages
    else:
        stages_to_run = [args.stage]

    # Execute pipeline
    try:
        success = pipeline.run_pipeline(
            stages_to_run=stages_to_run,
            resume=args.resume
        )

        # Report completion summary with warnings/errors highlighted
        final_success = pipeline._report_completion_summary(success)

        if final_success:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        pipeline.logger.warning("⚡ Pipeline interrupted by user")
        pipeline._report_completion_summary(False)
        sys.exit(130)
    except Exception as e:
        pipeline.logger.error(f"💥 Unexpected error: {e}")
        pipeline._report_completion_summary(False)
        sys.exit(1)

if __name__ == "__main__":
    main()