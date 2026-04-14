from fpdf import FPDF
import markdown
import re

def convert_to_pdf_bytes():
    md_text = """# Executive Summary 🤖\n## Key Insights 📉\n- **Hello** world\n"""
    # strip non latin-1 characters
    clean_text = md_text.encode('latin-1', 'ignore').decode('latin-1')
    html = markdown.markdown(clean_text)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.write_html(html)
    outbytes = pdf.output()
    print("Success:", type(outbytes))

if __name__ == "__main__":
    convert_to_pdf_bytes()
