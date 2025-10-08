#!/usr/bin/env python3
"""
Generate PDF versions of unit improvement emails from markdown files.

This module converts markdown-formatted unit improvement emails into professional
single-page PDF documents using WeasyPrint with custom CSS styling.

Inputs:
    - data/output/unit_emails/*.md: Markdown email files

Outputs:
    - data/output/unit_emails/*.pdf: Corresponding PDF files

Raises:
    FileNotFoundError: If input directory or markdown files don't exist
    PermissionError: If unable to write PDF files
"""

import sys
from pathlib import Path
from typing import List

import markdown
from weasyprint import HTML, CSS

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def get_pdf_css() -> str:
    """
    Generate CSS styling for single-page PDF layout.

    Returns:
        str: CSS stylesheet content for PDF generation

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
    """


def convert_markdown_to_pdf(markdown_file: Path, output_pdf: Path) -> None:
    """
    Convert a markdown file to PDF with professional styling.

    Args:
        markdown_file: Path to input markdown file
        output_pdf: Path for output PDF file

    Raises:
        FileNotFoundError: If markdown_file doesn't exist
        PermissionError: If unable to write output_pdf
    """
    # Parse unit info from filename: "Pack_7_Clinton_beascout_improvements.md"
    filename_parts = markdown_file.stem.replace('_beascout_improvements', '').split('_')

    header_html = ""
    if len(filename_parts) >= 3:
        unit_type = filename_parts[0]
        unit_number = filename_parts[1]
        unit_town = ' '.join(filename_parts[2:])

        header_html = f'''
        <div class="pdf-header">
            <h1>Heart of New England Council, Scouting America</h1>
            <h2>Be A Scout Improvements</h2>
            <h3>{unit_type} {unit_number} {unit_town}</h3>
        </div>
        <div class="pdf-separator"></div>
        '''

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

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['extra', 'nl2br']  # Support tables, fenced code, line breaks
    )

    # Wrap in basic HTML structure with header
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Unit Improvement Email</title>
    </head>
    <body>
        {header_html}
        {html_content}
    </body>
    </html>
    """

    # Generate PDF with custom CSS
    HTML(string=full_html).write_pdf(
        output_pdf,
        stylesheets=[CSS(string=get_pdf_css())]
    )


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
    """
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

    print(f"Converting {len(markdown_files)} markdown files to PDF...")

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
