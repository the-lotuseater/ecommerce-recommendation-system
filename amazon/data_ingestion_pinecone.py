from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from amazon.data_converter import DataConverter
from amazon.config import Config
import os

class DataIngestor:
    def __init__(self):
        self.embedding = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL
        )
        self.vector_store = PineconeVectorStore(
            embedding=self.embedding,
            index_name=Config.PINECONE_DB_INDEX
        )

    def ingest(self,load_existing=True):
        if load_existing:
            return self.vector_store
        converter = DataConverter(
            data_file_path=os.path.join("data", "Video_Games.json"),
            metadata_file_path=os.path.join("data", "meta_Video_Games.json"),
            merged_file_path=os.path.join("data", "merged_Video_Games.csv")
        )
        docs = converter.convert()
        batch_size = 32
        for i in range(0, len(docs), batch_size):
            self.vector_store.add_documents(docs[i:i+batch_size])
            print(f"Ingested {min(i+batch_size, len(docs))}/{len(docs)}")
        return self.vector_store
    
if __name__=='__main__':
    ingestor = DataIngestor()
    ingestor.ingest(load_existing=False)
