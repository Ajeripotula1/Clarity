import os, shutil
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

## This File initializes the Chroma Vector Database with an OpenAI embedding function ##
current_dir = os.path.dirname(os.path.abspath(__file__)) # get the current directory of the file
persistent_directory = os.path.join(current_dir,"db","chroma_db")   # define path to local db

# Create embeddings
print("\n--- Creating Embeddings ---")
embeddings = OpenAIEmbeddings ( model = "text-embedding-3-small" )
print("\n--- Finished creating embeddings ---")
            
# Initialize a persistent Chroma vectorstore
def get_db():
    print("\n--- Creating vector store ---") 
    vector_db = Chroma(
        persist_directory = persistent_directory,
        embedding_function = embeddings
    )
    print("\n--- Finished creating vector store ---") 
    return vector_db

# Delete in memory directory containing embeddings
def delete_db():
    if os.path.exists(persistent_directory):
        shutil.rmtree(persistent_directory)
        print("--- Chroma DB wiped ---")
    else:
        print("--- Chroma DB directory not found ---")
    