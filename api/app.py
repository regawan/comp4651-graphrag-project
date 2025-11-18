import shutil
import tempfile
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, UploadFile, File

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


@app.get("/graphrag/docs", response_model=ListDocsResponse)
def graphrag_list_docs():
    docs = service.list_documents()
    return ListDocsResponse(docs=docs)


@app.post("/graphrag/docs/add")
async def graphrag_add(files: List[UploadFile] = File(...)):
    """
    Upload one or more PDF files and ingest them into the GraphRAG pipeline.
    Note: adding pdf files can take some time!
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    temp_dir = tempfile.mkdtemp(prefix="graphrag_upload_")
    temp_paths: list[str] = []
    original_names: list[str] = []

    try:
        # Save uploaded files to temporary paths, ensure that they keep their original names
        for uploaded in files:
            original_name = Path(uploaded.filename).name
            original_names.append(original_name)

            suffix = Path(original_name).suffix or ".pdf"
            if not original_name.endswith(suffix):
                original_name = original_name + suffix

            dest_path = Path(temp_dir) / original_name

            content = await uploaded.read()
            with open(dest_path, "wb") as f:
                f.write(content)

            temp_paths.append(str(dest_path))

        # Pass the temp file paths into your existing ingestion method
        await service.build_knowledge_graph_from_pdfs(temp_paths)

        return {
            "status": "ok",
            "ingested": original_names
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up the temp directory
        try:
            shutil.rmtree(temp_dir)
        except OSError:
            pass


@app.delete("/graphrag/docs/{id}")
def graphrag_delete_doc(id: str):
    try:
        service.delete_document(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "deleted", "document_id": id}

@app.get("/health")
def health():
    return {"status": "ok"}
