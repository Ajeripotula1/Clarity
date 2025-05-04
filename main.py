import os
from db import get_db,delete_db
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_chroma import Chroma
from langchain.chains.summarize import load_summarize_chain

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
    # Define splitting parameters
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)    # Define Chunk size and overlap 
    
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
        # vector_db = get_db()
        vector_db.add_documents(docs)    
        return True 
    
    except Exception as e:
        print(f"Error processing document: {e}")
        return False

def summarize_file(file_name:str):
    ''' Generate Summary from all chunks that match input source
        Args:
            file_name: the document source we want to summarize
        Returns: 
            dictionary with answer and sources
    
    '''
    # Multi Page Summaries
    # Use Map Reduce:
        # Generate Summary of smaller chunks
        # Generate and return summary of summaries
    try:
        print(file_name)
        # query all releveant documents based on source
        results =  vector_db.get(where={"source": file_name})
        # convert retrieved dict into Dictionary Obj
        source_documents = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(results["documents"], results["metadatas"])
        ]
        # print(source_documents)
        # create summarizer chain
        # map
        map_prompt = '''
        Write a concise summary of the following:
        "{text}"
        CONCISE SUMMARY:
        '''
        map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])
        
        combine_prompt = """
            Write a concise summary of the following text delimited by triple backquotes.
            Return your response in bullet points which covers the key points of the text.
            ```{text}```
            BULLET POINT SUMMARY:
        """
        combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])

        
        """ Map Reduce
            - map reduce chain  first applies an LLM chain to each document individually (map)
            - treats the chain output as a new document
            - then passes all the new documents to a seperate combine documents chain (reduce)
            - finally a summary is generated based on these summaries of individual docs
        """
        summary_chain = load_summarize_chain(
            llm=model, 
            chain_type = "map_reduce", 
            map_prompt = map_prompt_template,
            combine_prompt_template = combine_prompt_template
            )
        summary = summary_chain.run(source_documents)
        # summary = summary_chain.invoke({"input_documents":source_documents})
        print(summary)
        return {
            "answer": summary,
            "sources": [file_name]
        }
        # create prompts
        # execute chain
        # return response to user
    except Exception as e:
        print(f"Error: {e}")

def answer_question_based_on_notes(query: str, chat_history: list) -> dict:
    ''' Answers questions based on notes alone and returns relevant chunks
        
        Args: 
            query (str): Users query to llm  
            chat_history (List): list of dictionaries containing conversation between AI and user
        
        Returns:
            dictionary with the answer and sources 
    '''
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
    system_msg = SystemMessage(content="You are a helpful assistant that answers questions strictly using the user's uploaded notes.") # Set system intent 
    
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
        You may reason and reference earlier parts of this conversation if helpful.
        If the answer is not found within the documents, respond with 'Answer not found in notes.'"""
    ))
    
    # Query LLM w/ chat history 
    response = model.invoke(messages)
    
    print("\n--- Generated Response ---")
    print(response.content)
    
    # Return Response content as well as relevant sources to API 
    return {
        "answer" : response.content,
        "sources" : sources
    }
    
    