from concurrent.futures import ThreadPoolExecutor
import uuid

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
    
    def upload_batch(self, texts, vectors, metadatas, i, total):
        records = [
            {"id": str(uuid.uuid4()), "values": vector, "metadata": {**metadata, "text": text}}
            for text, vector, metadata in zip(texts, vectors, metadatas)
        ]
        self.vector_store._index.upsert(vectors=records)
        print(f"Ingested {min(i + len(texts), total)}/{total}")

    def ingest_async(self, load_existing=True):
        if load_existing:
            return self.vector_store
        converter = DataConverter(
            data_file_path=os.path.join("data", "Video_Games.json"),
            metadata_file_path=os.path.join("data", "meta_Video_Games.json"),
            merged_file_path=os.path.join("data", "merged_Video_Games.csv")
        )
        docs = converter.convert()
        total = len(docs)
        embed_chunk = 1000
        upload_batch = 32

        for chunk_start in range(0, total, embed_chunk):
            chunk = docs[chunk_start:chunk_start + embed_chunk]
            texts = [doc.page_content for doc in chunk]
            metadatas = [doc.metadata for doc in chunk]
            print(f"Embedding docs {chunk_start}-{chunk_start + len(chunk)}...")
            vectors = self.embedding.embed_documents(texts)
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(
                        self.upload_batch,
                        texts[i:i+upload_batch],
                        vectors[i:i+upload_batch],
                        metadatas[i:i+upload_batch],
                        chunk_start + i,
                        total
                    )
                    for i in range(0, len(texts), upload_batch)
                ]
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Batch failed: {e}")
        print("Pipeline completed")
        return self.vector_store
    
if __name__=='__main__':
    ingestor = DataIngestor()
    ingestor.ingest_async(load_existing=False)
