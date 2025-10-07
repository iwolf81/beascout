#!/usr/bin/env python3
"""
Email Draft Generator for BeAScout Weekly Quality Reports
Creates complete email drafts with statistics for copy/paste distribution
Includes recipients, subject, body with analytics, and attachment info
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class EmailDraftGenerator:
    """Generates complete email drafts for weekly quality report distribution"""

    def __init__(self, scraped_session_id: str = None):
        self.analytics_data = None
        self.email_config = None
        self.scraped_session_id = scraped_session_id

    def load_email_configuration(self, config_path: Path = None) -> bool:
        """Load email distribution configuration"""
        if config_path is None:
            config_path = project_root / "data" / "config" / "email_distribution.json"

        if not config_path.exists():
            print(f"❌ Email configuration not found: {config_path}")
            return False

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.email_config = json.load(f)

            print(f"✅ Loaded email configuration: {config_path.name}")
            return True

        except Exception as e:
            print(f"❌ Error loading email configuration: {e}")
            return False

    def load_analytics_data(self, analytics_path: Path) -> bool:
        """Load weekly analytics data"""
        if not analytics_path.exists():
            print(f"❌ Analytics file not found: {analytics_path}")
            return False

        try:
            with open(analytics_path, 'r', encoding='utf-8') as f:
                self.analytics_data = json.load(f)

            print(f"✅ Loaded analytics data: {analytics_path.name}")
            return True

        except Exception as e:
            print(f"❌ Error loading analytics data: {e}")
            return False

    def find_latest_analytics(self, reports_dir: Path = None) -> Optional[Path]:
        """Find the most recent analytics file"""
        if reports_dir is None:
            reports_dir = project_root / "data" / "output" / "reports" / "weekly"

        if not reports_dir.exists():
            print(f"❌ Reports directory not found: {reports_dir}")
            return None

        # Find JSON files matching analytics pattern
        analytics_files = list(reports_dir.glob("BeAScout_Weekly_Quality_Report_*.json"))

        if not analytics_files:
            print(f"❌ No analytics files found in: {reports_dir}")
            return None

        # Return most recent by modification time
        latest_analytics = max(analytics_files, key=lambda p: p.stat().st_mtime)
        print(f"📊 Found latest analytics: {latest_analytics.name}")

        return latest_analytics

    def format_report_date(self, timestamp: str) -> str:
        """Format timestamp into readable date"""
        try:
            # Extract date part (YYYYMMDD) from timestamp
            date_str = timestamp[:8]
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            return date_obj.strftime("%B %d, %Y")
        except Exception:
            return timestamp

    def format_data_timestamp(self) -> str:
        """Format data timestamp - use scraped session timestamp if available, otherwise report timestamp"""
        try:
            # Prefer scraped session timestamp if available
            if self.scraped_session_id:
                # Parse scraped session timestamp: YYYYMMDD_HHMMSS
                date_part = self.scraped_session_id[:8]
                time_part = self.scraped_session_id[9:]

                date_obj = datetime.strptime(date_part, "%Y%m%d")
                time_obj = datetime.strptime(time_part, "%H%M%S")

                formatted_date = date_obj.strftime("%B %d, %Y")
                formatted_time = time_obj.strftime("%I:%M %p")

                return f"{formatted_date} at {formatted_time}"

            # Fall back to report timestamp from analytics
            metadata = self.analytics_data.get("report_metadata", {})
            timestamp = metadata.get("timestamp", "")

            if timestamp:
                # Parse timestamp: YYYYMMDD_HHMMSS
                date_part = timestamp[:8]
                time_part = timestamp[9:]

                date_obj = datetime.strptime(date_part, "%Y%m%d")
                time_obj = datetime.strptime(time_part, "%H%M%S")

                formatted_date = date_obj.strftime("%B %d, %Y")
                formatted_time = time_obj.strftime("%I:%M %p")

                return f"{formatted_date} at {formatted_time}"
            else:
                return "Date Unknown"

        except Exception:
            return "Date Unknown"

    def generate_statistics_section(self) -> str:
        """Generate the comprehensive statistics section for email body"""
        if not self.analytics_data:
            return "Statistics unavailable."

        comparison = self.analytics_data.get("weekly_comparison", {})
        exec_changes = comparison.get("executive_summary_changes", {})

        # Check if this is the first week
        if exec_changes.get("first_week", True):
            # First week - show current statistics without comparisons
            exec_summary = self.analytics_data.get("executive_summary", {})
            lines = ["This Week's Quality Overview:"]

            # Total units
            total_units = exec_summary.get("total_units")
            if total_units is not None:
                lines.append(f"• Total Units: {total_units} units")

            # Units missing from BeAScout
            missing_units = exec_summary.get("units_missing_from_beascout")
            if missing_units is not None:
                lines.append(f"• Units missing from BeAScout: {missing_units}")

            # Average quality score
            avg_score = exec_summary.get("average_quality_score")
            if avg_score is not None:
                lines.append(f"• Average Quality Score: {avg_score}%")

            # Complete grade distribution
            lines.append("• Quality Grade Distribution:")
            grade_dist = exec_summary.get("grade_distribution", {})
            grade_order = ["A", "B", "C", "D", "F", "N/A"]
            grade_names = {
                "A": "Grade A (90%+)",
                "B": "Grade B (80-89%)",
                "C": "Grade C (70-79%)",
                "D": "Grade D (60-69%)",
                "F": "Grade F (<60%)",
                "N/A": "Grade N/A (Missing)"
            }

            for grade in grade_order:
                if grade in grade_dist:
                    grade_data = grade_dist[grade]
                    count = grade_data.get("count")
                    percentage = grade_data.get("percentage")
                    if count is not None:
                        pct_str = f" ({percentage}%)" if percentage is not None else ""
                        lines.append(f"  - {grade_names[grade]}: {count} units{pct_str}")

            return "\n".join(lines)

        else:
            # Subsequent weeks - show comprehensive changes
            changes = exec_changes.get("changes", {})

            # Get baseline information
            baseline_info = comparison.get("baseline_metadata", {})
            baseline_date = baseline_info.get("baseline_date", "unknown")

            # Format baseline date for readability
            baseline_date_formatted = "unknown date"
            if baseline_date != "unknown" and len(baseline_date) == 8:
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(baseline_date, "%Y%m%d")
                    baseline_date_formatted = date_obj.strftime("%B %d, %Y")
                except:
                    baseline_date_formatted = baseline_date

            lines = [f"This Week's Quality Overview Changes (compared to {baseline_date_formatted} baseline):"]

            # Total units change
            if "total_units" in changes:
                total_data = changes["total_units"]
                current = total_data["current"]
                change = total_data["change"]
                sign = "+" if change >= 0 else ""
                lines.append(f"• Total Units: {current} units ({sign}{change} from baseline)")

            # Average quality score change
            if "average_quality_score" in changes:
                avg_data = changes["average_quality_score"]
                current = avg_data["current"]
                change = avg_data["change"]
                sign = "+" if change >= 0 else ""
                lines.append(f"• Average Quality Score: {current}% ({sign}{change}% from baseline)")

            # Complete grade distribution changes
            lines.append("• Quality Grade Distribution Changes:")
            grade_changes = changes.get("grade_distribution", {})
            grade_order = ["A", "B", "C", "D", "F", "N/A"]
            grade_names = {
                "A": "Grade A (90%+)",
                "B": "Grade B (80-89%)",
                "C": "Grade C (70-79%)",
                "D": "Grade D (60-69%)",
                "F": "Grade F (<60%)",
                "N/A": "Grade N/A (Missing)"
            }

            for grade in grade_order:
                if grade in grade_changes:
                    grade_data = grade_changes[grade]
                    current = grade_data["current"]
                    change = grade_data["change"]
                    sign = "+" if change >= 0 else ""
                    lines.append(f"  - {grade_names[grade]}: {current} units ({sign}{change} from baseline)")

            # Add unit-level changes
            unit_comparison = comparison.get("unit_score_changes", {})
            unit_changes = unit_comparison.get("unit_changes", [])

            if unit_changes:
                lines.append("")  # Empty line
                lines.append("Notable Unit Changes:")

                # Top improvements (up to 5)
                improvements = [u for u in unit_changes if u["improvement"]][:5]
                if improvements:
                    lines.append("Top Improvements:")
                    for unit in improvements:
                        prev_score = unit["previous_score"]
                        curr_score = unit["current_score"]
                        change = unit["change"]
                        lines.append(f"• {unit['unit_identifier']}: {prev_score}% → {curr_score}% (+{change}%)")
                else:
                    lines.append("Top Improvements:")
                    lines.append("• No unit improvements since baseline")

                lines.append("")  # Add spacing between improvements and declines

                # Top declines (up to 5)
                declines = [u for u in unit_changes if not u["improvement"]][:5]
                if declines:
                    lines.append("Top Declines:")
                    for unit in declines:
                        prev_score = unit["previous_score"]
                        curr_score = unit["current_score"]
                        change = unit["change"]
                        lines.append(f"• {unit['unit_identifier']}: {prev_score}% → {curr_score}% ({change}%)")
                else:
                    lines.append("Top Declines:")
                    lines.append("• No unit declines since baseline")

            return "\n".join(lines)

    def generate_email_draft(self, analytics_path: Path, output_path: Path = None) -> Path:
        """Generate complete email draft file"""
        # Load required data
        if not self.load_analytics_data(analytics_path):
            raise ValueError("Could not load analytics data")

        if not self.load_email_configuration():
            raise ValueError("Could not load email configuration")

        # Extract timestamp from analytics file for output naming
        metadata = self.analytics_data.get("report_metadata", {})
        timestamp = metadata.get("timestamp", datetime.now().strftime("%Y%m%d_%H%M%S"))

        # Determine output path
        if output_path is None:
            output_dir = analytics_path.parent
            output_path = output_dir / f"BeAScout_Weekly_Email_Draft_{timestamp}.txt"

        # Get configuration data
        recipients_list = self.email_config.get("distribution_lists", {}).get("leadership", [])
        sender_template = self.email_config.get("sender_template", {})
        email_template = self.email_config.get("email_templates", {}).get("weekly_quality_report", {})

        # Generate email components
        recipients_string = "; ".join(recipients_list)

        report_date = self.format_report_date(timestamp)
        subject = email_template.get("subject_template", "Weekly BeAScout Quality Report - {report_date}").format(
            report_date=report_date
        )

        statistics_section = self.generate_statistics_section()
        data_timestamp = self.format_data_timestamp()

        # Generate body from template
        body_template = email_template.get("body_template", "")
        body = body_template.format(
            statistics_section=statistics_section,
            data_timestamp=data_timestamp,
            sender_name=sender_template.get("name", "[Your Name]"),
            sender_title=sender_template.get("title", "[Your Title]"),
            sender_organization=sender_template.get("organization", "[Your Organization]")
        )

        # Get Excel filename
        excel_filename = metadata.get("excel_filename", f"BeAScout_Weekly_Quality_Report_{timestamp}.xlsx")

        # Build complete email draft
        email_draft = f"""=== EMAIL RECIPIENTS ===
{recipients_string}

=== EMAIL SUBJECT ===
{subject}

=== EMAIL BODY ===
{body}

=== ATTACHMENT ===
{excel_filename}

=== COPY/PASTE INSTRUCTIONS ===
1. Copy the recipients list above and paste into your email To: field
2. Copy the subject line above and paste into your email Subject: field
3. Copy the email body above and paste into your email body
4. Attach the Excel file listed above
5. Review and send

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # Save email draft
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(email_draft)

            print(f"✅ Email draft saved: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error saving email draft: {e}")
            raise

def main():
    """CLI interface for email draft generation"""
    parser = argparse.ArgumentParser(
        description="Generate email draft from weekly analytics",
        epilog="""
Examples:
  # Generate email draft from latest analytics
  python generate_weekly_email_draft.py

  # Generate email draft from specific analytics file
  python generate_weekly_email_draft.py --analytics-file path/to/analytics.json

  # Specify output location
  python generate_weekly_email_draft.py --output path/to/email_draft.txt

This script creates a complete email draft with recipients, subject,
body with statistics, and attachment information for copy/paste distribution.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--analytics-file', help='Path to analytics JSON file [default: find latest in weekly reports directory]')
    parser.add_argument('--output', help='Output path for email draft [default: same directory as analytics file]')
    parser.add_argument('--scraped-session', help='Scraped session ID for accurate data timestamp display')

    args = parser.parse_args()

    generator = EmailDraftGenerator(args.scraped_session)

    # Determine input analytics file
    if args.analytics_file:
        analytics_path = Path(args.analytics_file)
        if not analytics_path.exists():
            print(f"❌ Analytics file not found: {analytics_path}")
            sys.exit(1)
    else:
        analytics_path = generator.find_latest_analytics()
        if not analytics_path:
            print("❌ No analytics files found")
            sys.exit(1)

    # Determine output path
    output_path = Path(args.output) if args.output else None

    # Generate email draft
    try:
        result_path = generator.generate_email_draft(analytics_path, output_path)
        print(f"\n✅ Email draft generated successfully!")
        print(f"📁 Email draft file: {result_path}")
        print(f"\n📧 Ready for copy/paste distribution:")
        print(f"   1. Open: {result_path}")
        print(f"   2. Copy/paste recipients, subject, and body into your email client")
        print(f"   3. Attach the Excel file and send")

    except Exception as e:
        print(f"❌ Error generating email draft: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()