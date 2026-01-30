import os
import re
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from reportlab.platypus.flowables import PageBreak, KeepTogether
from reportlab.lib.utils import simpleSplit


def read_markdown_file(file_path):
    """Read the markdown file and return its content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def clean_text_for_pdf(text):
    """Clean text to remove or replace problematic Unicode characters."""
    replacements = {
        'φ': '(phi)',  # Greek phi
        '∑': 'sum',    # Summation symbol
        '∈': 'in',     # Element of
        '∀': 'for all', # For all
        '→': '->',     # Right arrow
        '≠': '!=',     # Not equal
        '≤': '<=',     # Less than or equal
        '≥': '>=',     # Greater than or equal
        '×': '*',      # Multiplication
        '∞': 'inf',    # Infinity
        'α': '(alpha)', # Greek alpha
        'β': '(beta)',  # Greek beta
        'γ': '(gamma)', # Greek gamma
        'δ': '(delta)', # Greek delta
        'ε': '(epsilon)', # Greek epsilon
        'θ': '(theta)', # Greek theta
        'λ': '(lambda)', # Greek lambda
        'μ': '(mu)',    # Greek mu
        'π': '(pi)',    # Greek pi
        'σ': '(sigma)', # Greek sigma
        'τ': '(tau)',   # Greek tau
        'Φ': '(Phi)',   # Greek Phi
        'Δ': 'Delta',   # Greek Delta
        'Γ': 'Gamma',   # Greek Gamma
        'Λ': 'Lambda',  # Greek Lambda
        'Ω': 'Omega',   # Greek Omega
        '√': 'sqrt',    # Square root
        '≈': '~=',      # Approximately equal
        '∝': 'prop',    # Proportional to
        '∇': 'del',     # Nabla/del operator
        '∂': 'partial', # Partial derivative
        '∫': 'int',     # Integral
        '∬': 'int2',    # Double integral
        '∭': 'int3',    # Triple integral
        '∮': 'contour', # Contour integral
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def parse_markdown_to_structure(content):
    """Parse markdown content into structured data."""
    lines = content.split('\n')
    structure = []
    current_section = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('---'):
            # Skip frontmatter
            i += 1
            while i < len(lines) and not lines[i].startswith('---'):
                i += 1
            i += 1
            continue
        
        if line.startswith('# '):
            # Main title
            title = line[2:].strip()
            structure.append({'type': 'title', 'content': title})
        elif line.startswith('## '):
            # Main heading
            heading = line[3:].strip()
            structure.append({'type': 'heading1', 'content': heading})
        elif line.startswith('### '):
            # Sub-heading
            heading = line[4:].strip()
            structure.append({'type': 'heading2', 'content': heading})
        elif line.startswith('**') and line.endswith('**') and ':' in line:
            # Bold key-value pairs
            structure.append({'type': 'bold', 'content': line.strip('* ')})
        elif line.startswith('|') and '|' in line:
            # Table
            table_data = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = [cell.strip() for cell in lines[i].strip('|').split('|')]
                table_data.append(row)
                i += 1
            structure.append({'type': 'table', 'content': table_data})
            i -= 1  # Adjust for the loop increment
        elif line.startswith('```'):
            # Code block
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            structure.append({'type': 'code', 'content': '\n'.join(code_lines)})
        elif line == '':
            # Empty line
            structure.append({'type': 'empty'})
        else:
            # Regular paragraph
            paragraph = line
            # Look ahead for continuation
            j = i + 1
            while j < len(lines) and lines[j].strip() != '' and not lines[j].strip().startswith('#') and not lines[j].strip().startswith('|') and not lines[j].strip().startswith('```'):
                paragraph += ' ' + lines[j].strip()
                j += 1
            
            structure.append({'type': 'paragraph', 'content': paragraph})
            i = j - 1  # Adjust index
        
        i += 1
    
    return structure


class ProfessionalWhitePaperPDF:
    def __init__(self, filename):
        self.filename = filename
        self.doc = SimpleDocTemplate(filename, pagesize=A4, 
                                   topMargin=72, bottomMargin=72, 
                                   leftMargin=72, rightMargin=72)
        self.styles = getSampleStyleSheet()
        self.elements = []
        
        # Create custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,  # Center alignment
            textColor=HexColor("#2C3E50"),
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,  # Center alignment
            textColor=HexColor("#34495E"),
            fontName='Helvetica'
        )
        
        self.metadata_style = ParagraphStyle(
            'Metadata',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=20,
            alignment=TA_CENTER,  # Center alignment
            textColor=colors.gray,
            fontName='Helvetica'
        )
        
        self.heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            borderWidth=0,
            borderColor=colors.black,
            borderPadding=0,
            textColor=HexColor("#2980B9"),
            fontName='Helvetica-Bold'
        )
        
        self.heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
            textColor=HexColor("#34495E"),
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=6,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            textColor=HexColor("#2C3E50")
        )
        
        self.bold_style = ParagraphStyle(
            'BoldStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=6,
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            textColor=HexColor("#2C3E50")
        )
        
        self.code_style = ParagraphStyle(
            'CodeStyle',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=9,
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=10,
            rightIndent=10,
            backColor=HexColor("#ECF0F1"),
            borderWidth=1,
            borderColor=HexColor("#BDC3C7"),
            borderPadding=5
        )
        
        # Create a header style
        self.header_style = ParagraphStyle(
            'Header',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.gray,
            fontName='Helvetica'
        )
    
    def create_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()
        
        # Header
        header = "A First-Principles Hybrid Attribution Framework"
        canvas.setFont('Helvetica', 10)
        canvas.drawString(inch, A4[1]-50, header)
        
        # Footer
        footer = f"Page {doc.page}"
        canvas.drawRightString(A4[0]-inch, 30, footer)
        
        canvas.restoreState()
    
    def add_title_page(self):
        """Add a professional title page."""
        # Add a cover page with a subtle background
        from reportlab.lib.colors import Color
        bg_color = Color(0.95, 0.95, 0.95, alpha=0.3)  # Light gray with transparency
        
        # Title
        title = Paragraph('A First-Principles Hybrid Attribution Framework', self.title_style)
        self.elements.append(title)
        
        subtitle = Paragraph('Integrating Probabilistic Path Modeling, Cooperative Game Theory, and Psychographic Transition Priors', self.title_style)
        self.elements.append(subtitle)
        
        # Subtitle
        subtitle_text = Paragraph('Technical Whitepaper v2.0.0', self.subtitle_style)
        self.elements.append(subtitle_text)
        
        # Add some space
        self.elements.append(Spacer(1, 20))
        
        # Organization info
        org_info = Paragraph(
            '<font size="12"><b>Advanced Analytics Division</b></font><br/>' +
            'First-Principles Attribution Engine Team',
            self.metadata_style
        )
        self.elements.append(org_info)
        
        # Add more space
        self.elements.append(Spacer(1, 20))
        
        # Metadata
        meta_text = Paragraph(
            'Classification: Methodology Specification / Decision Science<br/>' +
            'Status: Production-Ready / Frozen<br/>' +
            'Document Version: 2.0.0<br/>' +
            'Last Updated: January 23, 2026<br/>' +
            'Contact: attribution-engine@organization.com',
            self.metadata_style
        )
        self.elements.append(meta_text)
        
        # Add a decorative line
        self.elements.append(Spacer(1, 30))
        
        # Add page break
        self.elements.append(PageBreak())
    
    def add_content_from_structure(self, structure):
        """Add content to the PDF based on the parsed structure."""
        for item in structure:
            if item['type'] == 'title':
                cleaned_content = clean_text_for_pdf(item['content'])
                p = Paragraph(cleaned_content, self.title_style)
                self.elements.append(p)
            elif item['type'] == 'heading1':
                cleaned_content = clean_text_for_pdf(item['content'])
                p = Paragraph(cleaned_content, self.heading1_style)
                self.elements.append(p)
            elif item['type'] == 'heading2':
                cleaned_content = clean_text_for_pdf(item['content'])
                p = Paragraph(cleaned_content, self.heading2_style)
                self.elements.append(p)
            elif item['type'] == 'paragraph':
                cleaned_content = clean_text_for_pdf(item['content'])
                # Replace newlines with <br/> for ReportLab
                cleaned_content = cleaned_content.replace('\n', '<br/>')
                p = Paragraph(cleaned_content, self.normal_style)
                self.elements.append(p)
            elif item['type'] == 'bold':
                cleaned_content = clean_text_for_pdf(item['content'])
                p = Paragraph(f'<b>{cleaned_content}</b>', self.bold_style)
                self.elements.append(p)
            elif item['type'] == 'table':
                # Create table
                if len(item['content']) > 0:
                    # Clean table data
                    cleaned_table_data = []
                    for row in item['content']:
                        cleaned_row = [clean_text_for_pdf(str(cell)) for cell in row]
                        cleaned_table_data.append(cleaned_row)
                    
                    # Create the table
                    table = Table(cleaned_table_data)
                    
                    # Apply professional styling
                    table.setStyle(TableStyle([
                        # Header row styling
                        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#34495E")),  # Dark header
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        
                        # Body rows styling
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 1, HexColor("#BDC3C7")),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        
                        # Alternating row colors
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor("#F8F9FA")]),
                    ]))
                    
                    # Wrap in KeepTogether to prevent page breaks within tables
                    self.elements.append(KeepTogether([table]))
                    self.elements.append(Spacer(1, 15))  # Add space after table
            elif item['type'] == 'code':
                cleaned_content = clean_text_for_pdf(item['content'])
                p = Paragraph(f'<font face="Courier">{cleaned_content}</font>', self.code_style)
                self.elements.append(KeepTogether([p]))
            elif item['type'] == 'empty':
                self.elements.append(Spacer(1, 12))
    
    def save(self):
        """Build and save the PDF with custom header/footer."""
        # Register the header/footer function
        self.doc.build(self.elements, onFirstPage=self.create_header_footer, 
                      onLaterPages=self.create_header_footer)


def main():
    # Define file paths
    md_file_path = r"D:\first-principles-attribution-repo\docs\FIRST_PRINCIPLES_ATTRIBUTION_WHITEPAPER_PROFESSIONAL_FORMAT.md"
    final_pdf_path = r"D:\first-principles-attribution-repo\docs\FIRST_PRINCIPLES_ATTRIBUTION_WHITEPAPER_PROFESSIONAL_FORMAT_FINAL.pdf"
    
    # Read the markdown file
    content = read_markdown_file(md_file_path)
    
    # Parse the markdown content
    structure = parse_markdown_to_structure(content)
    
    # Create and save the final professional PDF
    print("Creating final professional PDF file...")
    pdf_writer = ProfessionalWhitePaperPDF(final_pdf_path)
    pdf_writer.add_title_page()
    pdf_writer.add_content_from_structure(structure)
    pdf_writer.save()
    print(f"Final professional PDF file saved to: {final_pdf_path}")
    
    print("\nFinal professional PDF creation completed successfully!")


if __name__ == "__main__":
    main()