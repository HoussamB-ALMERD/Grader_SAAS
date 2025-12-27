# app/parser.py
import os
import xml.etree.ElementTree as ET
import re

def extract_code_from_xml(content: str):
    try:
        root = ET.fromstring(content)
        lines = []
        for item in root.iter('item'):
            if item.get('algoitem'):
                lines.append(item.get('algoitem'))
        return "\n".join(lines)
    except:
        return ""

def process_student_zip(zip_path, extract_to):
    # Logic to unzip and map files to students
    # Returns a JSON structure: 
    # [ { "name": "John", "ex1": "code...", "ex2": "code..." } ]
    # (We will implement the full unzip logic in the main block for brevity)
    pass