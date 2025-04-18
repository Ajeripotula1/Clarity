import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

## This File initializes our Chroma Vector Database with an OpenAI embedding function ##
current_dir = os.path.dirname(os.path.abspath(__file__)) # get the current directory of the file
persistent_directory = os.path.join(current_dir,"db","chroma_db")   # define path to local db
    
# Create embeddings
print("\n--- Creating Embeddings ---")
embeddings = OpenAIEmbeddings ( model = "text-embedding-3-small" )
print("\n--- Finished creating embeddings ---")
            
# Initialize a persistent Chroma vectorstore
print("\n--- Creating vector store ---") 
vector_db = Chroma(
    persist_directory = persistent_directory,
    embedding_function = embeddings
)
print("\n--- Finished creating vector store ---") 
