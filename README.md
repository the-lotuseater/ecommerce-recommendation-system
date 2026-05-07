# Ecommerce Recommendation System

A conversational product recommendation chatbot built on real Amazon Video Games review data, powered by RAG (Retrieval Augmented Generation) and a Groq-hosted LLM.

---

## UI

**Landing screen** — ChatGPT-inspired search interface with suggestion chips for common queries.

![Home Screen](images/homescreen.png)

**Chat view** — multi-turn conversation with context-aware responses grounded in real user reviews.

![Reviews](images/reviews.png)

---

## How it works

### Embeddings

An embedding converts text into a list of numbers (a vector) that captures its semantic meaning. Words or sentences with similar meaning end up close together in this high-dimensional space — "Doom" and "FPS shooter" will be near each other, while "Doom" and "cooking game" will be far apart.

This project uses the `BAAI/bge-base-en-v1.5` model from HuggingFace, run locally via `sentence-transformers`. It produces a **768-dimensional dense vector** for each piece of text. During data ingestion, every review in the dataset is converted into one of these vectors and stored in Pinecone.

```
Review text  ──►  HuggingFace Embedding Model  ──►  [0.12, -0.84, 0.33, ...]  ──►  Pinecone
                  (BAAI/bge-base-en-v1.5)             768 numbers
```

### RAG — Retrieval Augmented Generation

A standard LLM only knows what it was trained on. RAG solves this by giving the model a relevant excerpt from your own data at query time, so its answer is grounded in real reviews rather than hallucinated.

The flow for every user question:

```
User question
     │
     ▼
Embed the question  (same model, same 768-dim space)
     │
     ▼
Pinecone similarity search  →  find the K most relevant reviews
     │
     ▼
Stuff reviews into a prompt  →  "Here are real reviews: [...]. Now answer: <question>"
     │
     ▼
Groq LLM (llama-3.1-8b-instant)  →  generates a grounded answer
     │
     ▼
Response returned to the user
```

Because the LLM sees the actual review text, it can make recommendations like "Based on reviews, I'd recommend Doom for FPS alien shooting" rather than guessing.

**History awareness** — the chain also maintains a per-session message history using `RunnableWithMessageHistory`, so follow-up questions like "tell me more about that one" resolve correctly.

---

## Data

Source: [UCSD Amazon Review Dataset](https://jmcauley.ucsd.edu/data/amazon/) — Video Games subset.

The dataset is split into two files: reviews (user ratings and text) and metadata (product titles, descriptions). Reviews do not contain a game title — only an `asin` product ID. A left join on `asin` brings the title in from the metadata file.

The merged dataset has ~50k rows. For development speed, only 5,000 rows are ingested into Pinecone (`max_docs=5000` in `data_converter.py`). Extending to the full dataset is straightforward by removing that cap.

The data pipeline lives in `amazon/data_converter.py`. Future work: convert this into an Airflow DAG for scheduled re-ingestion.

---

## Embedding reliability — why local over API

The project initially used the HuggingFace Inference API to generate embeddings remotely. This failed ~90% of the time due to rate limiting and server timeouts on the free tier. Switching to `HuggingFaceEmbeddings` from `langchain-huggingface` (which runs the model locally via `sentence-transformers`) eliminated all connectivity issues — the model is downloaded once and run on your machine for every subsequent ingestion.

Similarly, AstraDB was replaced with Pinecone after persistent connection failures. Pinecone's managed serverless index proved more reliable for development.

---

## Stack

| Layer | Technology |
|---|---|
| Embedding model | `BAAI/bge-base-en-v1.5` via `sentence-transformers` (local) |
| Vector store | Pinecone (serverless, dense, 768-dim) |
| LLM | Groq — `llama-3.1-8b-instant` |
| RAG orchestration | LangChain (`create_retrieval_chain`, `RunnableWithMessageHistory`) |
| Backend | Flask + flask-cors, Prometheus metrics on `/metrics` |
| Frontend | React + Vite (production build served via `serve`) |
| Containerisation | Docker (separate images for backend and frontend) |
| Orchestration | Kubernetes on GKE — Deployments, ClusterIP Services, GCE Ingress |
| Monitoring | Prometheus + Grafana (`monitoring` namespace) |

---

## Running locally

```bash
python application.py
```

This starts the Flask backend on port 5000 and the Vite dev server on port 3000.

Environment variables required in a `.env` file:

```
PINECONE_API_KEY=
PINECONE_DB_INDEX=
GROQ_API_KEY=
HUGGINGFACEHUB_API_TOKEN=
```

---

## Deployment (GKE)

```bash
# 1. Build and push images
docker build -t gcr.io/<project>/flask-app . -f backend/Dockerfile
docker build -t gcr.io/<project>/react-app ./frontend -f frontend/Dockerfile
docker push gcr.io/<project>/flask-app
docker push gcr.io/<project>/react-app

# 2. Create secrets
kubectl create secret generic shopbot-secrets --from-env-file=.env

# 3. Apply manifests
kubectl apply -f prometheus/namespace.yml
kubectl apply -f prometheus/
kubectl apply -f k8s/
```

The GCE Ingress routes `/chat` to the Flask service and `/` to the React service through a single GCP load balancer.
