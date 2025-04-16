from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from main import process_file_txt
import os, shutil
app = FastAPI()

class Item(BaseModel):
    text: str = None
    is_bool: bool = False
    
files = []

# Routes

# Upload File 
@app.post("/upload/")
# Expect a required file upload from a form, and when it comes in, treat it as a FastAPI UploadFile obj
def upload_file(file: UploadFile = File(...)):
    # Files we are capable of processing
    allowed_extensions = ['.txt']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if not file_extension in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsuported file type. Supported file types: {', '.join(allowed_extensions)}")
    temp_file_path = f"temp_{file.filename}"
    try:
        # Save the uploaded file to temporary file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file,buffer) # create a temp file and copy contents into it 
            
        success = process_file_txt(temp_file_path)
        if success:
            return {"message":f"File {file.filename} has been successfully uploaded"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename}.")
    finally: 
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    # contents = await file.read() # read file
    # text = contents.decode('utf-8') # decode into str
    
    # # Call LangChain Processing
    # result = process_file_txt(text, file.filename)
    
    # return {"status":"success", "result":result}

# View Files that were uploaded
