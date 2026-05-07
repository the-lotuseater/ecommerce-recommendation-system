from flask import Flask, request
from flask_cors import CORS
from prometheus_client import Counter, generate_latest
from amazon.data_ingestion_pinecone import DataIngestor
from amazon.rag_chain import RAGChainBuilder

rag_chain = None
app = Flask(__name__)
CORS(app)

def init():
    #assume data ingestion is complete
    vector_store = DataIngestor().ingest(load_existing=True)
    global rag_chain
    rag_chain = RAGChainBuilder(vector_store).build_chain()

@app.route("/chat", methods=["POST"])
def get_response():
    user_input = request.form['msg']
    response = rag_chain.invoke(
        { 'input':user_input },
        config = {'configurable':{'session_id':'user-session'}}
        )['answer']
    
    return response

def start_server():
    init()
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    start_server()