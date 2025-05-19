import os
from db import get_db,delete_db
from datetime import datetime,timedelta
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_chroma import Chroma
from langchain.chains.summarize import load_summarize_chain
import json,re

## This file handles the backend logic ##

# In-memory cache for storing recently generated content
summary_cache = {}
SUMMARY_TTL = timedelta(minutes=60)

load_dotenv()

## This File handles the backend logic called by the API Routes ## 

model = ChatOpenAI(model="gpt-3.5-turbo")

# VectorDB obj
vector_db = get_db()

# Returns list of files that the user uploaded
def get_all_sources() -> list[str]:
    # get all documents in vector database and their metadatas
    all_docs = vector_db.get()
    metadatas = all_docs.get("metadatas",[])
    # create list of 'source' values from the metadats
    files = [metadata.get("source") for metadata in metadatas if metadata]
    # return unique file names to user
    unique_files = list(set(files))
    print("Uploaded files:", unique_files)
    return unique_files

# Deletes all document chunks for the vector database that match the given file name
def delete_source(file_name : str) -> bool:
    try: 
        # Delete based on 'source' meatada
        vector_db.delete(where={"source": file_name})
        print(f"Deleted documents from file: {file_name}")
        return True
    except Exception as e:
        print(f"Error deleting documents for {file_name}: {e}")
        return False

# Chunk File and embedd content  
def process_file(file_path,file_name):
    # Intialize Loader based on file type
    extension = os.path.splitext(file_path)[1].lower()
    if extension =='.txt':
        loader = TextLoader(file_path=file_path)
    elif extension =='.pdf':
        loader = PyPDFLoader(file_path=file_path)
        
    # Define chunking parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=50,   # Define Chunk size and overlap 
        separators=["\n\n","\n", ".", " ",""])  # Define seperators to split text in order of preference
    try:
        documents = loader.load()
        # Split document into chunks and add 'source' and 'id' metadata to each chunk
        docs = []
        for i, chunk in enumerate(text_splitter.split_documents(documents)):
            docs.append(Document(
                page_content = chunk.page_content,
                metadata={"source":file_name}, # Add Metadata
                id=f"{file_path}-{i}" # prevent adding duplicate chunks    
                )
            )
                 
        # Display information about the split documents
        print("\n--- Document Chunks Information ---\n")
        print(f"Number of document chunks: {len(docs)}")
        print(f"Sample chunk:\n{docs[0].page_content}\n")
            
        # Add new documents to exisiting vector store
        vector_db.add_documents(docs)    
        return True 
    
    except Exception as e:
        print(f"Error processing document: {e}")
        return False

# Answer questions based on notes and returns relevant chunks
def answer_question_based_on_notes(query: str, chat_history: list) -> dict:
    # Setup Vector Store Retriever to retrieve relevant docs based on query
    retriever = vector_db.as_retriever(
        search_type = 'similarity', # return chunks based on semantic similarity
        search_kwargs = {"k":3} # specify how many chunks to return
    )
    relevant_docs = retriever.invoke(query)
    
    # Display relevant results with the metadata
    print("\n-- Relevant Documents --")
    for i, doc in enumerate(relevant_docs,1):
        print(f"Document {i}, {doc.page_content}")
        
    # Construct input for LLM
    sources = [doc.page_content for doc in relevant_docs]
    context = "\n\n".join(sources) # join relevant pages
    system_msg = SystemMessage(content="You are a helpful assistant that answers questions mainly using the user's uploaded notes.") # Set system intent 
    
    # Build the chat history
    messages = [system_msg]
    for turn in chat_history:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        elif turn["role"] == "assistant":
            messages.append(AIMessage(content=turn["content"]))
    
    # Add user's query to chat history
    messages.append(HumanMessage(
        content=f"""Here are some docuements that might help answer the question: {query}
        \n\nRelevant documents:\n{context}\n\n Answer the question primarily using the information in the provided documents. 
        You may reason and reference earlier parts of this conversation if helpful.'"""
    ))
    
    # Query LLM w/ chat history 
    response = model.invoke(messages)
    
    print("\n--- Generated Response ---")
    print(response.content)
    
    # Return Response content as well as relevant to API 
    return {
        "answer" : response.content,
    }

# Generate Summary from all chunks that match input source
def summarize_file(file_name:str):
    # Multi Page Summaries
    # Use Map Reduce:
        # Generate Summary of smaller chunks
        # Generate and return summary of summaries
    try:
        # check if summary exists in the cache 
        now = datetime.now()
        cached = summary_cache.get(file_name)
        
        # check if summary is cached and recent
        if cached and now-cached["timestamp"] < SUMMARY_TTL:
            print("*** SUMMARY EXISTS IN CACHE ***")
            return {
                "answer": cached["summary"]
            }
        
        # Otherwise, generate and cache the summary
        print("*** GENERATING SUMMARY ***")    
        
        # query all releveant documents based on source
        results =  vector_db.get(where={"source": file_name})
        # convert retrieved dict into Document Obj
        source_documents = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(results["documents"], results["metadatas"])
        ]
        
        # Define Map Prompt
        map_prompt = """
            You're reviewing notes. Extract valuable content in the following structure in a clear, study-friendly format:

            💡 Big Ideas:
            - Extract the most important insights or ideas.
            
            📘 Key Terms & Definitions:
            - List any terms defined in this chunk. Format: **Term**: definition.

            🔄 Summary:
            - A one-sentence summary of this chunk.

            Note:
            \"\"\"{text}\"\"\"
            """
        # Create the prompt and pass input text
        map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])
        
        # Define Prompt to combine summaries of each page/chunk
        combine_prompt = """
            You are summarizing extracted notes from multiple chunks. Organize your response with the following structure to promote study and learning for the user.:

            ### 💡 **Big Ideas:**
            - Merge big ideas across chunks into bullet points. Avoid repetition.
            
            ### 📘 **Key Terms & Definitions:**
            - Combine and deduplicate key terms. Format: **Term**: definition.

           ### 🔄 **Final Summary:**
            - A 2–3 sentence high-level summary.

            Chunks:
            \"\"\"{text}\"\"\"
            """
        # Create Combine prompt and pass text
        combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])

        # Create a map reduce chain
        """ Map Reduce:
            - map reduce chain first applies an LLM chain to each document individually (map)
            - treats the chain output as a new document
            - then passes all the new documents to a seperate combine documents chain (reduce)
            - finally a summary is generated based on these summaries of individual docs
        """
        # Define and invoke the chain
        summary_chain = load_summarize_chain(
            llm=model, 
            chain_type = "map_reduce", 
            map_prompt = map_prompt_template,
            combine_prompt = combine_prompt_template
            )
        summary = summary_chain.invoke(source_documents)
        print(summary['output_text'])
        
        # cache the summary, and return output
        summary_cache[file_name] = {
            "summary": summary['output_text'],
            "timestamp": now
        }
        return {
            "answer": summary['output_text'],
        }
      
    except Exception as e:
        print(f"Error: {e}")

# Generate Flashcards (question and answer pairs) based on summaries
def generate_flash_cards(file_name:str) -> list[dict]:
    
    # check if summary exisits in cache, generate otherwise 
    summary = summarize_file(file_name)
    flashcard_prompt = f"""
        Based on the following summary of a document, generate 15 flashcards in JSON format. Each flashcard should have a **concise question and answer** that helps the user study key ideas asnd definitions from the summary.
        
        Return a list of flashcards like this:
        [
            {{"question": "...", "answer": "..."}}
            ...
        ]
        
        Summary:
        \"\"\"{summary['answer']}\"\"\"
        """
    response = model.invoke(flashcard_prompt)
    print(response.content)
    
    # Parse the JSON string into a list of dicts
    content = response.content.strip()
    # Strip code block if present (e.g., ```json ... ```)
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

    try:
        flashcards = json.loads(content)
    except Exception as e:
        raise ValueError(f"Invalid JSON from model: {e}\n\nRaw content: {response.content}")

    return {"flash_cards": flashcards}
        