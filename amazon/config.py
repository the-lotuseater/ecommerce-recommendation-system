from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    ASTRA_DB_ENDPOINT = os.getenv('ASTRA_DB_API_ENDPOINT')
    HUGGINGFACEHUB_API_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    ASTRA_DB_APP_TOKEN = os.getenv('ASTRA_DB_APP_TOKEN')
    ASTRA_DB_KEYSPACE = os.getenv('ASTRA_DB_KEYSPACE')
    EMBEDDING_MODEL = 'BAAI/bge-base-en-v1.5'
    RAG_MODEL = 'llama-3.1-8b-instant'
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_DB_ENDPOINT = os.getenv('PINECONE_DB_ENDPOINT')
    PINECONE_DB_KEYSPACE = os.getenv('PINECONE_DB_KEYSPACE')
    PINECONE_DB_INDEX = os.getenv('PINECONE_DB_INDEX')