from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from main import process_file, answer_question_based_on_notes, get_all_sources, delete_source, summarize_file, generate_flash_cards
import os, shutil
from typing import List, Literal

## This file handles our API Routes ##

app = FastAPI(
    title="Clarity API",
    description="Upload docs, ask questions, generate summaries and flashcards.",
    version='1.0.0'
)
    
## Define Models ##
class ListResponse(BaseModel): # List of all document names
    file_names : List[str]
    
class ChatTurn(BaseModel): # Single Chat Message (Turn)
    role: Literal['user','assistant'] # Who is  speaking (user or AI)
    content: str    # What they said (query or response)

class QueryRequest (BaseModel): # Query Sent to API
    query: str  # current question being asked
    chat_history: List[ChatTurn]    # List of previous messages to preserve context 

class QueryResponse(BaseModel): # Structure of LLM response 
    answer: str # LLM response
   
# Requesting delete, summary, or flashcards for a specific file    
class FileRequest(BaseModel):
    file_name : str
    
class DeleteResponse(BaseModel):
    success : bool    

class QAPair(BaseModel):
    question: str
    answer: str
    
# takes in the document name and returns list of QA pairs in JSON format 
class FlashCards(BaseModel):
    flash_cards: List[QAPair]
    
## Routes ##

@app.post("/upload") # Upload File 
# Expect a required file upload from a form, and when it comes in, treat it as a FastAPI UploadFile obj
def upload_file(file: UploadFile = File(...)):
    """ Allows users to upload files

    Args:
        file (UploadFile, optional): File object.

    Raises:
        HTTPException 400: File type unsupported
        HTTPException 500: File upload failed

    Returns:
        Success Message
    """
    # Files we are capable of processing
    allowed_extensions = ['.txt','.pdf']
    file_name = os.path.splitext(file.filename)[0].lower()
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if not file_extension in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsuported file type. Supported file types: {', '.join(allowed_extensions)}")
    
    temp_file_path = f"temp_{file.filename}"
    
    try:
        # Save the uploaded file to temporary buffer 
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file,buffer) # create a temp file and copy contents into it 
            
        # file_content
        success = process_file(temp_file_path,file_name) # Call function to embed and store document
        
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
    """
    Context based conversation w/ the LLM based on uploaded docuements

    Args:
        payload (QueryRequest): User's query (str) and chat history (List[str])

    Raises:
        HTTPException 500: if LLM coud not produce a response

    Returns:
        QueryResponse: The LLM's reply to query based on chat context
    """
    try:
        print("Chat History: ", payload.chat_history)
        result = answer_question_based_on_notes(
            query = payload.query, # pass query to LLM
            chat_history = [{"role": turn.role, "content": turn.content} for turn in payload.chat_history]
        ) 
        return QueryResponse(answer=result["answer"])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model = ListResponse, tags=["List all Docs"])
def get_files():
    """
    Retrieves all unique documents present in the vector database
    
    Args: None
    
    Raises:
        HTTPException 500: if could not retrieve documents
        
    Returns:
        - ListResponse: a list of all document names
    """
    try:
        result = get_all_sources()
        return ListResponse(file_names=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@app.post("/delete", response_model= DeleteResponse, tags=["Delete"])
def delete_file(doc: FileRequest):
    """
    Deletes all document chunks related to a specific file.

    Args:
        doc (DeleteRequest): Object containing the file name to delete

    Returns:
        DeleteResponse: Boolean flag indicating whether deletion was successful.
    """
    try:
        result = delete_source(doc.file_name)
        return DeleteResponse(success=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

@app.post("/summarize", response_model=QueryResponse, tags=["Summarize"])
def summarize(doc: FileRequest):
    """
    Generate indepth summaries of documents

    Args:
        doc (FileRequest): The file the user wants the summary of

    Raises:
        HTTPException 500: If error while generating the summary

    Returns:
        QueryResponse: The LLM's response containing the summary
    """
    try:
        response = summarize_file(doc.file_name)
        return QueryResponse(answer=response["answer"])
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@app.post(path = "/flashcards", response_model=FlashCards, tags=["Flashcards"])
def create_flashcards(doc: FileRequest):
    """
    Generate "flashcards"(question and answer pairs) based on documents

    Args:
        doc (FileRequest): The documen name

    Raises:
        HTTPException 500: If error generating the flashcards

    Returns:
        Flashcards: Q&A pairs
    """
    try:
        response = generate_flash_cards(doc.file_name)
        return FlashCards(flash_cards = response.get("flash_cards",[]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    