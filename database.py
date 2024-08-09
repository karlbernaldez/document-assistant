from pymongo import MongoClient
from datetime import datetime, timedelta
from logger import setup_logger

# Set up logger
logger = setup_logger(__name__)

class MongoDBHandler:
    def __init__(self, uri='mongodb+srv://adovelopers:hk6JVl0ajdDdMuCY@eazeye.hgfph5o.mongodb.net/?retryWrites=true&w=majority&appName=Eazeye', db_name='pdf_document_assistant'):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def initialize_database(self):
        try:
            logger.info("Initializing MongoDB database.")
            # In MongoDB, the database and collections are created automatically when data is inserted
            logger.info("MongoDB database initialized.")
        except Exception as e:
            logger.error(f"Error initializing MongoDB database: {e}")

    def save_chunks_to_mongodb(self, chunks, title, file_size, processing_time, num_chunks):
        try:
            logger.info("Saving text chunks to MongoDB.")
            document = {
                "title": title,
                "file_size": file_size,
                "processing_time": processing_time,
                "num_chunks": num_chunks,
                "chunks": [chunk.page_content for chunk in chunks],
                "timestamp": datetime.now()
            }
            self.db.documents.insert_one(document)
            logger.info("Text chunks saved to MongoDB.")
        except Exception as e:
            logger.error(f"Error saving chunks to MongoDB: {e}")

    def get_documents_by_date(self, query_date):
        try:
            logger.info(f"Fetching documents uploaded on {query_date}.")
            start_date = datetime.strptime(query_date, "%Y-%m-%d")
            end_date = start_date + timedelta(days=1)
            documents = self.db.documents.find({"timestamp": {"$gte": start_date, "$lt": end_date}})
            results = [(doc["title"], doc["file_size"], doc["processing_time"], doc["num_chunks"], doc["tokens_count"]) for doc in documents]
            logger.info(f"Found {len(results)} documents uploaded on {query_date}.")
            return results
        except Exception as e:
            logger.error(f"Error fetching documents by date: {e}")
            return []

    def is_document_uploaded(self, title):
        try:
            print(f"Checking if document '{title}' is already uploaded.")
            logger.info(f"Checking if document '{title}' is already uploaded.")
            count = self.db.documents.count_documents({"title": title})
            print(f"Document '{title}' is already uploaded: {count > 0}.")
            logger.info(f"Document '{title}' is already uploaded: {count > 0}.")
            return count > 0
        except Exception as e:
            logger.error(f"Error checking if document is uploaded: {e}")
            return False

# Create an instance of the handler
db_handler = MongoDBHandler(uri='mongodb+srv://adovelopers:hk6JVl0ajdDdMuCY@eazeye.hgfph5o.mongodb.net/?retryWrites=true&w=majority&appName=Eazeye')
