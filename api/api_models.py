from typing import Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str


class DocInfo(BaseModel):
    document_id: Optional[str] # str or None
    chunks: int

class ListDocsResponse(BaseModel):
    docs: list[DocInfo]