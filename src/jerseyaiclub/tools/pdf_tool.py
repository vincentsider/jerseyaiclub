from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from fpdf import FPDF
import os

class PDFToolInput(BaseModel):
    content: str = Field(..., description="Content to write to the PDF file")
    filename: str = Field(..., description="Name of the PDF file to create")

class PDFTool(BaseTool):
    name: str = "PDF Creator"
    description: str = "Creates a PDF document"
    args_schema: Type[BaseModel] = PDFToolInput

    def _run(self, content: str, filename: str) -> str:
        # Setup PDF
        pdf = FPDF()
        pdf.set_doc_option('core_fonts_encoding', 'windows-1252')
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_margins(20, 20, 20)
        
        # Process content line by line
        lines = content.split('\n')
        in_table = False
        table_data = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if not in_table:
                    pdf.ln(5)
                continue
            
            # Workflow Title
            if line.startswith('**') and 'Workflow' in line and not line.endswith(':**'):
                if pdf.get_y() > 250:
                    pdf.add_page()
                pdf.set_font('Arial', 'B', 14)
                pdf.ln(10)
                pdf.cell(0, 10, line.strip('*'), ln=True)
                
            # Workflow Summary (line after title)
            elif line and not line.startswith('**') and not line.startswith('|') and not line[0].isdigit() and not line.startswith('Time saved:'):
                pdf.set_font('Arial', 'I', 12)
                pdf.ln(5)
                pdf.multi_cell(0, 10, line)
                pdf.ln(5)
                
            # Section Headers
            elif line.startswith('**') and line.endswith(':**'):
                pdf.set_font('Arial', 'B', 12)
                pdf.ln(5)
                pdf.cell(0, 10, line.strip('*:'), ln=True)
                pdf.set_font('Arial', '', 12)
                
            # Table
            elif line.startswith('|'):
                if not in_table:
                    in_table = True
                    table_data = []
                if '--|--' not in line:  # Skip separator line
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]
                    if cells:
                        table_data.append(cells)
                    
            # End of table
            elif in_table and table_data:
                if pdf.get_y() > 250:
                    pdf.add_page()
                
                # Two equal columns
                col_width = (pdf.w - 40) / 2
                
                # Header
                pdf.set_font('Arial', 'B', 12)
                for cell in table_data[0]:
                    pdf.cell(col_width, 10, cell, 1, 0, 'C')
                pdf.ln()
                
                # Data
                pdf.set_font('Arial', '', 12)
                for row in table_data[1:]:
                    if len(row) >= 2:
                        # Handle multi-line cells
                        lines1 = [row[0][i:i+30] for i in range(0, len(row[0]), 30)]
                        lines2 = [row[1][i:i+30] for i in range(0, len(row[1]), 30)]
                        max_lines = max(len(lines1), len(lines2))
                        height = max(10, max_lines * 5)
                        
                        xstart = pdf.get_x()
                        ystart = pdf.get_y()
                        
                        # First column
                        pdf.multi_cell(col_width, height/max_lines, row[0], 1, 'L')
                        pdf.set_xy(xstart + col_width, ystart)
                        
                        # Second column
                        pdf.multi_cell(col_width, height/max_lines, row[1], 1, 'L')
                        
                        if pdf.get_y() < ystart + height:
                            pdf.set_y(ystart + height)
                
                in_table = False
                table_data = []
                pdf.ln(5)
                
            # Time saved
            elif line.startswith('Time saved:'):
                pdf.set_font('Arial', 'B', 12)
                pdf.ln(5)
                pdf.cell(0, 10, line, ln=True)
                pdf.ln(10)  # Extra space after time saved
                
            # Numbered steps
            elif line[0].isdigit() and line[1] == '.':
                if pdf.get_y() > 250:
                    pdf.add_page()
                pdf.set_font('Arial', '', 12)
                pdf.cell(10)  # Indent
                pdf.multi_cell(0, 10, line)
                
            # Regular text
            else:
                if not in_table:  # Skip if we're collecting table data
                    if pdf.get_y() > 250:
                        pdf.add_page()
                    pdf.set_font('Arial', '', 12)
                    pdf.multi_cell(0, 10, line)
        
        # Save PDF
        pdf_dir = os.path.join(os.getcwd(), "pdf")
        os.makedirs(pdf_dir, exist_ok=True)
        filepath = os.path.join(pdf_dir, filename)
        if not filename.endswith('.pdf'):
            filepath += '.pdf'
            
        try:
            pdf.output(filepath, 'F')  # Force binary mode
            return f"PDF created at {filepath}"
        except Exception as e:
            # Try with different encoding if first attempt fails
            pdf.set_doc_option('core_fonts_encoding', 'utf-8')
            pdf.output(filepath, 'F')
            return f"PDF created at {filepath} with UTF-8 encoding"
