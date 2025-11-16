from fastapi import FastAPI

from api.api_models import QueryResponse, QueryRequest, ListDocsResponse
from backend.graphrag_config import GraphRAGConfig
from backend.graphrag_service import GraphRAGService
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

config = GraphRAGConfig.from_env()
service = GraphRAGService(config)

@app.post("/graphrag/query", response_model=QueryResponse)
def graphrag_query(payload: QueryRequest):
    answer = service.query(payload.question, top_k=payload.top_k)
    return QueryResponse(answer=answer)

@app.get("/graphrag/list-docs", response_model=ListDocsResponse)
def graphrag_list_docs():
    docs = service.list_documents()
    return ListDocsResponse(docs=docs)

@app.get("/health")
def health():
    return {"status": "ok"}
