#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Academic PDF Generator for RBRU AgriPhysics Research Manuscripts
Converts Markdown manuscripts to Masterclass print-ready PDFs (A4, 28mm gutter, MathJax/KaTeX, booktabs tables)
using Pandoc and Headless Chrome.
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path

WORKSPACE = Path("/Users/chewathassana/Downloads/spectrometer_npk2026").resolve()
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PANDOC_BIN = "/opt/homebrew/bin/pandoc"
PDFINFO_BIN = "/opt/homebrew/bin/pdfinfo"

CSS_PATH = WORKSPACE / "research_papers" / "build" / "academic_print.css"
BUILD_DIR = WORKSPACE / "research_papers" / "build"
CHROME_PROFILE = BUILD_DIR / "chrome_profile"

MANUSCRIPTS = [
    {
        "id": "paper1_root",
        "name": "Paper 1 (Q1 Phosphorus Modeling - Root Folder)",
        "input_md": WORKSPACE / "research_q1_phosphorus" / "manuscript_q1_phosphorus_modelling.md",
        "output_pdf": WORKSPACE / "research_q1_phosphorus" / "manuscript_q1_phosphorus_modelling.pdf",
        "cwd": WORKSPACE / "research_q1_phosphorus",
    },
    {
        "id": "paper1_catalog",
        "name": "Paper 1 (Q1 Phosphorus Modeling - Research Papers Catalog)",
        "input_md": WORKSPACE / "research_papers" / "paper1_phosphorus_q1" / "manuscript_q1_phosphorus_modelling.md",
        "output_pdf": WORKSPACE / "research_papers" / "paper1_phosphorus_q1" / "manuscript_q1_phosphorus_modelling.pdf",
        "cwd": WORKSPACE / "research_papers" / "paper1_phosphorus_q1",
    },
    {
        "id": "paper2",
        "name": "Paper 2 (Q1/Q2 Nitrogen Multi-Tier)",
        "input_md": WORKSPACE / "research_papers" / "paper2_nitrogen_q1_q2" / "manuscript_nitrogen_multitier.md",
        "output_pdf": WORKSPACE / "research_papers" / "paper2_nitrogen_q1_q2" / "manuscript_nitrogen_multitier.pdf",
        "cwd": WORKSPACE / "research_papers" / "paper2_nitrogen_q1_q2",
    },
    {
        "id": "paper3",
        "name": "Paper 3 (Q2/TCI1 Soil Matrix Recovery)",
        "input_md": WORKSPACE / "research_papers" / "paper3_soil_matrix_recovery" / "manuscript_soil_matrix_recovery.md",
        "output_pdf": WORKSPACE / "research_papers" / "paper3_soil_matrix_recovery" / "manuscript_soil_matrix_recovery.pdf",
        "cwd": WORKSPACE / "research_papers" / "paper3_soil_matrix_recovery",
    },
    {
        "id": "paper4",
        "name": "Paper 4 (TCI1/2 Portable Hardware & Orchard Trials)",
        "input_md": WORKSPACE / "research_papers" / "paper4_portable_hardware_tci1" / "manuscript_portable_spectrometer_tci.md",
        "output_pdf": WORKSPACE / "research_papers" / "paper4_portable_hardware_tci1" / "manuscript_portable_spectrometer_tci.pdf",
        "cwd": WORKSPACE / "research_papers" / "paper4_portable_hardware_tci1",
    },
]


def convert_md_to_html(input_md: Path, output_html: Path, cwd: Path):
    """Convert Markdown manuscript to standalone HTML with MathJax and print CSS."""
    # Ensure custom HTML head with MathJax config and CSS
    cmd = [
        PANDOC_BIN,
        str(input_md.resolve()),
        "-s",
        "--mathjax=https://cdn.jsdelivr.net/npm/mathjax@4/tex-chtml.js",
        "--css", str(CSS_PATH.resolve()),
        "-f", "markdown+pipe_tables+tex_math_dollars+raw_html",
        "-t", "html5",
        "-o", str(output_html.resolve())
    ]
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error converting {input_md} to HTML:\n{res.stderr}")
        return False
    
    # Post-process HTML to ensure MathJax renders cleanly before print
    html_content = output_html.read_text(encoding="utf-8")
    
    # Inject MathJax ready script before </head>
    mathjax_hook = """
<script>
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
    processEscapes: true
  },
  startup: {
    pageReady: () => {
      return MathJax.startup.defaultPageReady().then(() => {
        document.body.classList.add('mathjax-rendered');
      });
    }
  }
};
</script>
"""
    if "</head>" in html_content:
        html_content = html_content.replace("</head>", f"{mathjax_hook}\n</head>")
        output_html.write_text(html_content, encoding="utf-8")

    return True


def render_html_to_pdf(input_html: Path, output_pdf: Path):
    """Render HTML to PDF using Chrome Headless with process control."""
    if output_pdf.exists():
        output_pdf.unlink()
        
    chrome_cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-software-rasterizer",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-sync",
        "--disable-default-apps",
        "--no-first-run",
        f"--user-data-dir={CHROME_PROFILE}",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=5000",
        f"--print-to-pdf={output_pdf.resolve()}",
        "--no-pdf-header-footer",
        f"file://{input_html.resolve()}"
    ]
    
    proc = subprocess.Popen(chrome_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Poll for PDF creation and stabilization
    max_wait = 18 # seconds
    start_time = time.time()
    pdf_ready = False
    last_size = -1
    
    while time.time() - start_time < max_wait:
        if output_pdf.exists():
            curr_size = output_pdf.stat().st_size
            if curr_size > 50000 and curr_size == last_size:
                pdf_ready = True
                break
            last_size = curr_size
        time.sleep(0.5)
        
    # Terminate Chrome
    try:
        proc.terminate()
        proc.wait(timeout=2)
    except Exception:
        proc.kill()
        
    return pdf_ready and output_pdf.exists()


def get_pdf_info(pdf_path: Path):
    """Extract page count and size using pdfinfo."""
    if not pdf_path.exists():
        return "Not found"
    size_kb = pdf_path.stat().st_size / 1024
    cmd = [PDFINFO_BIN, str(pdf_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    pages = "?"
    for line in res.stdout.splitlines():
        if "Pages:" in line:
            pages = line.split(":", 1)[1].strip()
    return f"{pages} pages ({size_kb:.1f} KB)"


def main():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    CHROME_PROFILE.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("RBRU AgriPhysics Research Manuscripts - Academic PDF Compiler")
    print("=" * 70)
    
    success_count = 0
    results = []
    
    for item in MANUSCRIPTS:
        name = item["name"]
        input_md = item["input_md"]
        output_pdf = item["output_pdf"]
        cwd = item["cwd"]
        temp_html = BUILD_DIR / f"{item['id']}.html"
        
        print(f"\n[Processing] {name}")
        print(f"  Markdown: {input_md}")
        
        if not input_md.exists():
            print(f"  [ERROR] File not found: {input_md}")
            results.append((name, "Input missing", False))
            continue
            
        print("  -> Converting to HTML...")
        if not convert_md_to_html(input_md, temp_html, cwd):
            results.append((name, "HTML conversion failed", False))
            continue
            
        print("  -> Rendering PDF via Chrome Headless...")
        ok = render_html_to_pdf(temp_html, output_pdf)
        if ok:
            info = get_pdf_info(output_pdf)
            print(f"  [SUCCESS] {output_pdf.name} generated: {info}")
            results.append((name, info, True))
            success_count += 1
        else:
            print(f"  [ERROR] PDF rendering failed for {output_pdf.name}")
            results.append((name, "PDF rendering failed", False))

    print("\n" + "=" * 70)
    print("COMPILATION SUMMARY")
    print("=" * 70)
    for name, info, ok in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{status} | {name} : {info}")
        
    print(f"\nTotal completed: {success_count}/{len(MANUSCRIPTS)}")
    if success_count == len(MANUSCRIPTS):
        print("All research papers have been successfully compiled to print-ready PDF!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
