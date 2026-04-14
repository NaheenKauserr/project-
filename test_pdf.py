from fpdf import FPDF
import markdown

def convert_to_pdf():
    md_text = """# Executive Summary
## Key Insights
- **Hello** world
- Test *italics*
"""
    html = markdown.markdown(md_text)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    # write_html is available in fpdf2
    pdf.write_html(html)
    pdf.output("test_report.pdf")

if __name__ == "__main__":
    convert_to_pdf()
