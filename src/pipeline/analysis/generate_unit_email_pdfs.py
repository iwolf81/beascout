#!/usr/bin/env python3
"""
Generate PDF versions of unit improvement emails from markdown files.

This module converts markdown-formatted unit improvement emails into professional
single-page PDF documents using Pandoc with custom CSS styling.

Inputs:
    - data/output/unit_emails/*.md: Markdown email files

Outputs:
    - data/output/unit_emails/*.pdf: Corresponding PDF files

Requirements:
    - Pandoc must be installed (brew install pandoc or apt-get install pandoc)

Raises:
    FileNotFoundError: If input directory or markdown files don't exist
    PermissionError: If unable to write PDF files
    RuntimeError: If pandoc is not installed or execution fails
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import List

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def check_pandoc_installed() -> bool:
    """
    Check if pandoc is installed and accessible.

    Returns:
        bool: True if pandoc is available, False otherwise
    """
    try:
        result = subprocess.run(
            ['pandoc', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_pdf_css() -> str:
    """
    Generate CSS styling for single-page PDF layout.

    Returns:
        str: CSS stylesheet content for PDF generation via Pandoc

    Design:
        - Single page constraint with controlled margins
        - Professional typography with readable font sizes
        - Clean spacing and visual hierarchy
        - Compact layout to fit content on one page
    """
    return """
        @page {
            size: letter;
            margin: 0.5in 0.75in;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 10pt;
            line-height: 1.3;
            color: #333;
            max-width: 100%;
        }

        .pdf-header {
            text-align: center;
            margin-bottom: 16pt;
        }

        .pdf-header h1 {
            font-size: 14pt;
            margin: 0;
            color: #003f87;
            font-weight: bold;
            border-bottom: none;
        }

        .pdf-header h2 {
            font-size: 14pt;
            margin: 0;
            color: #003f87;
            font-weight: bold;
            border-top: none;
        }

        .pdf-header h3 {
            font-size: 14pt;
            margin: 0;
            color: #003f87;
            font-weight: bold;
            padding-top: 4pt;
        }

        .pdf-separator {
            border-top: 2px solid #ce1126;
            margin: 0 0 16pt 0;
        }

        h1 {
            font-size: 14pt;
            margin: 0 0 8pt 0;
            color: #003f87;
            border-bottom: 2px solid #ce1126;
            padding-bottom: 4pt;
        }

        h2 {
            font-size: 12pt;
            margin: 10pt 0 6pt 0;
            color: #003f87;
        }

        h3 {
            font-size: 11pt;
            margin: 8pt 0 4pt 0;
            color: #444;
        }

        p {
            margin: 4pt 0;
        }

        ul, ol {
            margin: 4pt 0;
            padding-left: 20pt;
        }

        li {
            margin: 2pt 0;
        }

        strong {
            color: #000;
        }

        hr {
            border: none;
            border-top: 1px solid #ccc;
            margin: 8pt 0;
        }

        /* Compact spacing for recommendation sections */
        h2 + h3 {
            margin-top: 4pt;
        }

        /* Prevent awkward breaks */
        h2, h3 {
            page-break-after: avoid;
        }

        ul, ol {
            page-break-inside: avoid;
        }

        /* Table styling for contact information */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 8pt 0;
        }

        td {
            padding: 6pt 12pt;
            vertical-align: top;
            width: 50%;
        }

        td:first-child {
            padding-right: 24pt;
        }
    """


def convert_markdown_to_pdf(markdown_file: Path, output_pdf: Path) -> None:
    """
    Convert a markdown file to PDF with professional styling using Pandoc.

    Args:
        markdown_file: Path to input markdown file
        output_pdf: Path for output PDF file

    Raises:
        FileNotFoundError: If markdown_file doesn't exist
        PermissionError: If unable to write output_pdf
        RuntimeError: If pandoc execution fails
    """
    if not markdown_file.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_file}")

    # Parse unit info from filename: "Pack_7_Clinton_beascout_improvements.md"
    filename_parts = markdown_file.stem.replace('_beascout_improvements', '').split('_')

    header_markdown = ""
    if len(filename_parts) >= 3:
        unit_type = filename_parts[0]
        unit_number = filename_parts[1]
        unit_town = ' '.join(filename_parts[2:])

        header_markdown = f"""---
title: "Heart of New England Council, Scouting America"
subtitle: "Be A Scout Improvements"
author: "{unit_type} {unit_number} {unit_town}"
---

"""

    # Read markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Strip everything PRIOR to "**Dear" line (keeping "**Dear" and everything after)
    lines = md_content.split('\n')
    cleaned_lines = []
    found_dear = False

    for line in lines:
        # Once we find the "Dear" line, keep it and everything after
        if not found_dear:
            if line.strip().startswith('**Dear ') or line.strip().startswith('Dear '):
                found_dear = True
                cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)

    md_content = '\n'.join(cleaned_lines)

    # Combine header and content
    full_markdown = header_markdown + md_content

    # Create temporary files for markdown and CSS
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
        temp_md.write(full_markdown)
        temp_md_path = temp_md.name

    with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False, encoding='utf-8') as temp_css:
        temp_css.write(get_pdf_css())
        temp_css_path = temp_css.name

    try:
        # Run pandoc to convert markdown to PDF
        cmd = [
            'pandoc',
            temp_md_path,
            '--css', temp_css_path,
            '--pdf-engine=wkhtmltopdf',  # Use wkhtmltopdf for CSS support
            '-o', str(output_pdf),
            '--standalone'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            # If wkhtmltopdf not available, try default engine
            if 'wkhtmltopdf not found' in result.stderr.lower():
                cmd = [
                    'pandoc',
                    temp_md_path,
                    '-o', str(output_pdf),
                    '--standalone'
                ]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

            if result.returncode != 0:
                raise RuntimeError(f"Pandoc failed: {result.stderr}")

    finally:
        # Clean up temporary files
        try:
            os.unlink(temp_md_path)
            os.unlink(temp_css_path)
        except:
            pass


def process_all_unit_emails(input_dir: Path, output_dir: Path = None) -> List[Path]:
    """
    Convert all markdown unit emails to PDF format.

    Args:
        input_dir: Directory containing markdown email files
        output_dir: Directory for PDF output (defaults to same as input_dir)

    Returns:
        List of generated PDF file paths

    Raises:
        FileNotFoundError: If input_dir doesn't exist
        RuntimeError: If pandoc is not installed
    """
    if not check_pandoc_installed():
        raise RuntimeError(
            "Pandoc is not installed or not in PATH. "
            "Install with: brew install pandoc (macOS) or apt-get install pandoc (Linux)"
        )

    if output_dir is None:
        output_dir = input_dir

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all markdown files
    markdown_files = sorted(input_dir.glob("*.md"))

    if not markdown_files:
        print(f"⚠️  No markdown files found in {input_dir}")
        return []

    generated_pdfs = []

    print(f"Converting {len(markdown_files)} markdown files to PDF using Pandoc...")

    for md_file in markdown_files:
        # Generate PDF filename
        pdf_file = output_dir / f"{md_file.stem}.pdf"

        try:
            convert_markdown_to_pdf(md_file, pdf_file)
            generated_pdfs.append(pdf_file)
            print(f"✅ {pdf_file.name}")
        except Exception as e:
            print(f"❌ Failed to convert {md_file.name}: {e}")

    print(f"\n✅ Generated {len(generated_pdfs)} PDF files in {output_dir}")
    return generated_pdfs


def main():
    """Main execution: Convert unit email markdowns to PDFs."""
    # Define paths
    input_dir = project_root / "data" / "output" / "unit_emails"

    # Process all emails
    generated_pdfs = process_all_unit_emails(input_dir)

    if generated_pdfs:
        print(f"\n📄 Sample output: {generated_pdfs[0]}")


if __name__ == "__main__":
    main()
