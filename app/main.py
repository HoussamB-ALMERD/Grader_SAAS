from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import os
import zipfile
from pathlib import Path
from app.parser import extract_code_from_xml

app = FastAPI()

# Mounts
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/parse")
async def parse_files(student_zip: UploadFile = File(...), 
                      ref_ex1: UploadFile = File(...),
                      ref_ex2: UploadFile = File(...),
                      ref_ex3: UploadFile = File(...),
                      ref_ex4: UploadFile = File(...)):
    
    # 1. Save and Unzip Students
    zip_path = UPLOAD_DIR / "students.zip"
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(student_zip.file, buffer)
    
    extract_path = UPLOAD_DIR / "extracted"
    if extract_path.exists(): shutil.rmtree(extract_path)
    extract_path.mkdir()
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    # 2. Parse References
    refs = {}
    for i, file in enumerate([ref_ex1, ref_ex2, ref_ex3, ref_ex4], 1):
        content = (await file.read()).decode('utf-8')
        refs[f"Ex{i}"] = extract_code_from_xml(content)

    # 3. Scan & Parse Students (Reusing our Regex Logic)
    payload = []
    
    # Recursive walk to find folders
    for root, dirs, files in os.walk(extract_path):
        if "CP1_TP_EXAM_ALG" in root: # Loose check for student folder
            folder_name = os.path.basename(root)
            parts = folder_name.split('_')
            name = f"{parts[0]} {parts[1]}" if len(parts) > 1 else folder_name
            
            student_obj = {"name": name, "submissions": {}}
            
            for f in files:
                if f.endswith('.alg'):
                    # Simple Number detection
                    num_match = re.search(r'[1-4]', f)
                    if num_match:
                        num = num_match.group(0)
                        file_path = os.path.join(root, f)
                        with open(file_path, 'r', encoding='utf-8') as alg_file:
                            clean_code = extract_code_from_xml(alg_file.read())
                            student_obj["submissions"][f"Ex{num}"] = clean_code
            
            payload.append(student_obj)

    # Return the clean data to the browser
    return {"references": refs, "students": payload}