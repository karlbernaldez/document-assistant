import os
import time
import warnings
from microphone import select_microphone
from chatbot import chat_bot
from docs_process import load_existing_chunks, save_chunks_cache
from database import db_handler
from logger import setup_logger
from pinecone import Pinecone, ServerlessSpec
from transformers import pipeline
from google.cloud import documentai_v1beta3 as documentai
from google.oauth2 import service_account

# Suppress FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning)

# Set up logger
logger = setup_logger(__name__)

# Set environment variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./eazeye-ai-310068fbd361.json"
os.environ["OPENAI_API_KEY"] = "api key"

# Initialize Pinecone
api_key = "Api key"
pc = Pinecone(api_key=api_key)

# Create Pinecone index if it doesn't exist
index_name = "document-index"
dimension = 768  # Replace with the dimension of your embeddings
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

# Connect to the index
index = pc.Index(index_name)

# Initialize embedding model
embedding_model = pipeline("feature-extraction", model="distilbert-base-uncased")

def setup_environment():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./eazeye-ai-310068fbd361.json"
    os.environ["OPENAI_API_KEY"] = "api key"

def process_document_with_api(file_path):
    credentials = service_account.Credentials.from_service_account_file("./eazeye-ai-0cfaa1eb5886.json")
    client = documentai.DocumentProcessorServiceClient(credentials=credentials)
    project_id = "eazeye-ai"
    location = "us"
    processor_id = "your-processor-id"
    with open(file_path, "rb") as document:
        document_content = document.read()
    request = {
        "name": f"projects/{project_id}/locations/{location}/processors/{processor_id}",
        "raw_document": {"content": document_content, "mime_type": "application/pdf"},
    }
    result = client.process_document(request=request)
    document = result.document
    text_chunks = [page.text for page in document.pages]
    return text_chunks

def get_embeddings(text):
    return embedding_model(text)[0]

def add_documents_to_index(documents):
    vectors = [(str(i), get_embeddings(doc)) for i, doc in enumerate(documents)]
    index.upsert(vectors)

def load_or_process_chunks(new_document_path):
    if new_document_path.lower() != 'skip':
        start_time = time.time()
        new_text_chunks = process_document_with_api(new_document_path)
        title = new_document_path.split("/")[-1]  # Simplified title extraction
        processing_time = time.time() - start_time
        file_size = os.path.getsize(new_document_path)
        num_chunks = len(new_text_chunks)
        logger.info(f"Processed document '{title}' in {processing_time:.2f} seconds with file size {file_size} bytes and {num_chunks} chunks.")

        document_uploaded = db_handler.is_document_uploaded(title)
        logger.info(f"Document '{title}' upload status: {document_uploaded}")

        if not document_uploaded:
            db_handler.save_chunks_to_mongodb(new_text_chunks, title, file_size, processing_time, num_chunks)
            return new_text_chunks, False
        else:
            logger.info(f"Document '{title}' is already uploaded.")
            return [], True
    return [], False

if __name__ == "__main__":
    setup_environment()
    all_text_chunks = load_existing_chunks()

    new_document_path = input("Enter the path to the new PDF document or type 'skip' to skip: ")
    if new_document_path.lower() != 'skip':
        new_text_chunks, document_uploaded = load_or_process_chunks(new_document_path)
        if new_text_chunks:
            all_text_chunks.extend(new_text_chunks)
            save_chunks_cache(all_text_chunks)

            # Add new documents to Pinecone index
            add_documents_to_index(new_text_chunks)

    mic_index = select_microphone()
    chat_bot(mic_index, None, db_handler)
