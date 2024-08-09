import os
import pickle
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from logger import setup_logger
from tqdm import tqdm
import sys
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Set up logger
logger = setup_logger(__name__)

chunks_cache_path = "text_chunks.pkl"

def load_existing_chunks():
    """
    Load existing chunks from cache.
    
    Returns:
        list: A list of text chunks.
    """
    logger.info("Loading existing chunks from cache.")
    try:
        if os.path.exists(chunks_cache_path):
            with open(chunks_cache_path, 'rb') as f:
                chunks = pickle.load(f)
                logger.info("Loaded chunks from cache.")
                return chunks
        logger.info("No existing chunks found in cache.")
        return []
    except Exception as e:
        logger.error(f"Error loading chunks from cache: {e}")
        return []

def save_chunks_cache(chunks):
    """
    Save chunks to cache.
    
    Args:
        chunks (list): List of text chunks to be saved.
    """
    logger.info("Saving chunks to cache.")
    try:
        with open(chunks_cache_path, 'wb') as f:
            pickle.dump(chunks, f)
        logger.info("Chunks saved to cache successfully.")
    except Exception as e:
        logger.error(f"Error saving chunks to cache: {e}")

def extract_title(documents):
    """
    Extract title from the first document.
    
    Args:
        documents (list): List of documents.
    
    Returns:
        str: The extracted title or "Unknown Title" if not found.
    """
    if documents and len(documents) > 0:
        title = documents[0].page_content.split('\n')[0]
        logger.info(f"Extracted title: {title}")
        return title
    logger.warning("No documents found to extract title.")
    return "Unknown Title"

def process_new_document(new_document_path):
    """
    Process a new document and split it into text chunks.
    
    Args:
        new_document_path (str): Path to the new document.
    
    Returns:
        tuple: A tuple containing the text chunks and the document title.
    """
    logger.info(f"Processing new document from path: {new_document_path}")
    try:
        loader = UnstructuredFileLoader(new_document_path)
        documents = loader.load()
        title = extract_title(documents)
        text_splitter = CharacterTextSplitter(separator='/n', chunk_size=5000, chunk_overlap=200)
        text_chunks = text_splitter.split_documents(documents)
        logger.info(f"Processed document '{title}' into {len(text_chunks)} chunks.")
        return text_chunks, title
    except Exception as e:
        logger.error(f"Error processing document '{new_document_path}': {e}")
        return [], "Unknown Title"

def process_documents_with_progress(document_paths):
    """
    Process multiple documents with progress tracking.
    
    Args:
        document_paths (list): List of document paths to be processed.
    
    Returns:
        list: A list of results from processing each document.
    """
    results = []
    for path in tqdm(document_paths, desc="Processing documents", file=sys.stdout):
        try:
            results.append(process_new_document(path))
        except Exception as e:
            logger.error(f"Error processing document '{path}': {e}")
    return results

def initialize_qa_chain(knowledge_base):
    """
    Initialize the QA chain using the provided knowledge base.
    
    Args:
        knowledge_base: The knowledge base for QA.
    
    Returns:
        RetrievalQA: The initialized QA chain.
    """
    from chatbot import initialize_qa_chain as cb_initialize_qa_chain
    return cb_initialize_qa_chain(knowledge_base)
