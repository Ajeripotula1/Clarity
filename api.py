from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from main import process_file, answer_question_based_on_notes
import os, shutil
from typing import List, Literal

## This file handles our API Routes ##

app = FastAPI()
    
# Define Models
class ChatTurn(BaseModel): # Single Chat Message (Turn)
    role: Literal['user','assistant'] # Who is  speaking (user or AI)
    content: str    # What they said (query or response)

class QueryRequest (BaseModel): # Query Sent to API
    query: str  # current question being asked
    chat_history: List[ChatTurn]    # List of previous messages to preserve context 

class QueryResponse(BaseModel): # Structure of backend response 
    answer: str # LLM response
    sources : List[str] # Source documents or chunks 

# Routes 
@app.post("/upload") # Upload File 
# Expect a required file upload from a form, and when it comes in, treat it as a FastAPI UploadFile obj
def upload_file(file: UploadFile = File(...)):
    # Files we are capable of processing
    allowed_extensions = ['.txt','.pdf']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if not file_extension in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsuported file type. Supported file types: {', '.join(allowed_extensions)}")
    
    temp_file_path = f"temp_{file.filename}"
    
    try:
        # # Save the uploaded file to temporary file (Streamlit doesn't requre saving file in memory)
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file,buffer) # create a temp file and copy contents into it 
            
        # file_content
        success = process_file(temp_file_path) # Call function to embed and store document
        
        if success:
            return {"message":f"File {file.filename} has been successfully uploaded"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename}.")
        
    finally: 
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
@app.post("/chat", response_model=QueryResponse, tags=["Chat"])
# parse JSON body and validate against QueryRequest model and return python obj
async def query_llm(payload: QueryRequest): 
    '''
    Args:
        payload (QueryRequest): Contains 'query' (str) and optional 'chat_history' (List[dict])
    
    Returns:
        QueryResponse: Contains the assistant's reply and source chunks.
    '''
    try:
        print("Chat History: ", payload.chat_history)
        result = answer_question_based_on_notes(
            query = payload.query, # pass query to LLM
            chat_history = [{"role": turn.role, "content": turn.content} for turn in payload.chat_history]
            # chat_history=[{"role": turn.role, "content": turn.content} for turn in payload.chat_history] # pass chat history
        ) 
        return QueryResponse(answer=result["answer"], sources = result.get("sources",[]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
            
# @app.post("/ask", response_model=QueryResponse, tags=["Ask"]) # Allow user to send query to LLM after uploading notes
# # parse JSON body and validate against QueryRequest model and return python obj
# async def query_llm(payload: QueryRequest): 
#     try:
#         result = answer_question_based_on_notes(payload.query) # pass query to LLM
#         return QueryResponse(answer=result["answer"], sources = result.get("sources",[]))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


