from fpdf import FPDF
import markdown

def convert_to_pdf_bytes():
    md_text = """# Executive Summary\n## Key Insights\n- **Hello** world\n"""
    html = markdown.markdown(md_text)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.write_html(html)
    outbytes = pdf.output()  # In fpdf2 passing nothing returns a bytearray
    with open("test2.pdf", "wb") as f:
        f.write(bytes(outbytes))
    print(type(outbytes), len(outbytes))

if __name__ == "__main__":
    convert_to_pdf_bytes()
