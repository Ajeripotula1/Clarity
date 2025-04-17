# 1. make a simple openAI call to makesure langchain and openAI are working
import os
from db import vector_db
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma

load_dotenv()

## This File handles the backend logic called by the API Routes ## 

model = ChatOpenAI(model="gpt-3.5-turbo")

messages = [
    SystemMessage("You are a helpful assistant"),
    HumanMessage("How to learn to code?")
]

# Chunk File and embedd content  
def process_file(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)    # Define Chunk size and overlap 
    
    try:
        # Handle txt file logic
        if extension == ".txt":
            loader = TextLoader(file_path=file_path)
            documents = loader.load()
            
            # Split document into chunks and add 'source' and 'id' metadata to each chunk
            docs = []
            for i, chunk in enumerate(text_splitter.split_documents(documents)):
                docs.append(Document(
                    page_content = chunk.page_content,
                    metadata={"source":file_path}, # Add Metadata
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

def answer_question_based_on_notes(query: str):
    '''Answers questions based on notes alone and returns relevant chunks'''
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
        
    sources = [doc.page_content for doc in relevant_docs]
    # Combine the query and relevant documents for LLM to answer
    combined_input = (
        "Here are some documents that might help answer the question: " # Inform the LLM about the query and documents
        + query
        + "\n\nRelevant documents:\n\n"
        + "\n\n".join(sources) # Attach the relevant documents
        # Instruct LLM to answer ONLY based on exisiting notes
        +"\n\nPlease Provide an answer based on ONLY the provided documents. If the answer is not found within the documents, respond with 'Answer not found in notes'."
    )
    # Define the messages for the model
    messages =  [
        SystemMessage(content="You are a helpful Note taking app assistant that answer questions based on the user's documents"),
        HumanMessage(content=combined_input)
    ]
    
    # Invoke the model and return the response
    response = model.invoke(messages)
    # Display the full result and content only
    print("\n--- Generated Response ---")
    # print("Full result:")
    # print(result)
    print("Content only:")
    print(response.content)
    
    # Return Response content as well as relevant sources to API 
    return {
        "answer" : response.content,
        "sources" : sources
    }
