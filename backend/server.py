from flask import Flask, request, Response
from flask_cors import CORS
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from amazon.data_ingestion_pinecone import DataIngestor
from amazon.rag_chain import RAGChainBuilder

rag_chain = None
app = Flask(__name__)
CORS(app)

chat_requests_total = Counter('chat_requests_total', 'Total number of chat requests')

def init():
    #assume data ingestion is complete
    vector_store = DataIngestor().ingest(load_existing=True)
    global rag_chain
    rag_chain = RAGChainBuilder(vector_store).build_chain()

@app.route('/health')
def health_probe():
    return 'OK'

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/chat", methods=["POST"])
def get_response():
    chat_requests_total.inc()
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