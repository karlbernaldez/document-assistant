from dateutil import parser
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from datetime import datetime, timedelta
import re
import time
from logger import setup_logger
from transcribe import transcribe_audio
from tts import text_to_speech_stream, play_audio_stream, CHARACTER_LIMIT, EXCEEDING_TEXT

# Set up logger
logger = setup_logger(__name__)

llm = ChatOpenAI(model="gpt-4o-mini", api_key="API KEY")

def is_asking_for_uploaded_documents(question):
    logger.info(f"Checking if question is about uploaded documents: '{question}'")
    response = llm.invoke(f"Only answer Yes or No. Is the following question asking about documents uploaded on a specific date? '{question}'")
    is_about_documents = "yes" in response.content.strip().lower()
    logger.info(f"Question about uploaded documents: {is_about_documents}")
    return is_about_documents

def extract_date_from_question(question):
    try:
        if 'today' in question.lower():
            date = datetime.now().strftime('%Y-%m-%d')
            logger.info(f"Extracted date 'today': {date}")
            return date
        elif 'yesterday' in question.lower():
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            logger.info(f"Extracted date 'yesterday': {date}")
            return date

        date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4})\b)')
        match = date_pattern.search(question)
        if match:
            date_str = match.group(0)
            date = parser.parse(date_str).strftime('%Y-%m-%d')
            logger.info(f"Extracted date from question: {date}")
            return date
        else:
            logger.warning("No date found in the question.")
            return None
    except (ValueError, IndexError) as e:
        logger.error(f"Error extracting date from question: {e}")
        return None

def initialize_qa_chain(knowledge_base):
    logger.info("Initializing QA chain.")
    return RetrievalQA.from_chain_type(llm, retriever=knowledge_base.as_retriever())

def answer_question(qa_chain, question):
    logger.info(f"Answering question: {question}")
    response = qa_chain.invoke({"query": question})
    num_tokens = len(response["result"].split())
    logger.info(f"Processed {num_tokens} tokens.")
    return response

def chat_bot(mic_index, qa_chain, db_handler):
    print("Welcome to the document-based chatbot! Ask your questions about the document.")
    print("Type 'exit' to end the chat.")
    while True:
        question = transcribe_audio(mic_index)
        if question and question.lower() == 'exit':
            logger.info("Chatbot session ended by user.")
            print("Goodbye!")
            break
        if question and is_asking_for_uploaded_documents(question):
            query_date = extract_date_from_question(question)
            if query_date:
                documents = db_handler.get_documents_by_date(query_date)
                if documents:
                    print(f"\nDocuments uploaded on {query_date}:")
                    for doc in documents:
                        print(f"{doc[0]} (File Size: {doc[1]} bytes, Processing Time: {doc[2]} seconds, Chunks: {doc[3]}, Tokens: {doc[4]})")
                else:
                    print(f"\nNo documents found for the date: {query_date}")
            else:
                print("\nInvalid date format. Please try again with a date in the format 'uploaded on <date>'.")
        elif question:
            start_time = time.time()
            response = answer_question(qa_chain, question)
            processing_time = time.time() - start_time
            num_tokens = len(response["result"].split())

            logger.info(f"Answered question in {processing_time:.2f} seconds, processing {num_tokens} tokens.")
            print("\nAnswer:")
            print(response["result"])

            # Convert response to speech and play it
            try:
                audio_stream = text_to_speech_stream(response["result"])
                play_audio_stream(audio_stream)
            except ValueError as e:
                print(f"Error: {e}")
                logger.error(f"Error: {e}")
