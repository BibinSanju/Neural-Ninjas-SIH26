import json
import os
from docx import Document
from openpyxl import Workbook

async def generate_word_document(title: str, content: str, filepath: str) -> str:
    """
    Generates a Word document with the given title and markdown-like content.
    For simplicity, we handle basic text paragraphs.
    """
    try:
        doc = Document()
        doc.add_heading(title, level=1)
        
        # Split content by newlines and add as paragraphs
        # A full implementation would parse markdown into bold/italic/headings
        for line in content.split('\n'):
            if line.strip():
                if line.startswith('## '):
                    doc.add_heading(line[3:], level=2)
                elif line.startswith('### '):
                    doc.add_heading(line[4:], level=3)
                elif line.startswith('- '):
                    doc.add_paragraph(line[2:], style='List Bullet')
                else:
                    doc.add_paragraph(line)
                    
        doc.save(filepath)
        return f"Successfully generated Word document at {os.path.abspath(filepath)}"
    except Exception as e:
        return f"Failed to generate Word document: {str(e)}"

async def generate_excel_spreadsheet(data_json: str, filepath: str) -> str:
    """
    Generates an Excel spreadsheet from a JSON string representing an array of objects.
    """
    try:
        data = json.loads(data_json)
        if not isinstance(data, list) or not data:
            return "Error: data_json must be a non-empty JSON array of objects."
            
        wb = Workbook()
        ws = wb.active
        
        # Extract headers from the first object
        headers = list(data[0].keys())
        ws.append(headers)
        
        # Add rows
        for item in data:
            row = [item.get(h, "") for h in headers]
            ws.append(row)
            
        wb.save(filepath)
        return f"Successfully generated Excel spreadsheet at {os.path.abspath(filepath)}"
    except json.JSONDecodeError:
        return "Failed to parse data_json. Ensure it is valid JSON."
    except Exception as e:
        return f"Failed to generate Excel spreadsheet: {str(e)}"
