# 1. make a simple openAI call to makesure langchain and openAI are working
import os
from db import vector_db
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
load_dotenv()

model = ChatOpenAI(model="gpt-3.5-turbo")

messages = [
    SystemMessage("You are a helpful assistant"),
    HumanMessage("How to learn to code?")
]

# response = model.invoke(messages)
# print(response.content)

# Chunk File and embedd content  
def process_file_txt(file_path):
    
    
    extension = os.path.splitext(file_path)[1].lower()
    
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)    # Define Chunk size and overlap 
    
    print("\n--- Finished creating vector store ---") 
    try:
        # Handle txt file logic
        if extension == ".txt":
            loader = TextLoader(file_path=file_path)
            documents = loader.load()
            
            # Split document into chunks
            docs = []
            for i, chunk in enumerate(text_splitter.split_documents(documents)):
                docs.append(Document(
                    page_content = chunk.page_content,
                    metadata={"source":file_path},
                    id=f"{file_path}-{i}" # prevent adding duplicate chunks    
                    )
                )
                # Add Metadata 
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

