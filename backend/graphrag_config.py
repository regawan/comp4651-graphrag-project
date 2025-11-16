import os
from dataclasses import dataclass

@dataclass
class GraphRAGConfig:
    vertex_ai_project_id: str
    vertex_ai_location: str
    vertex_ai_account_key_path: str | None

    neo4j_uri: str
    neo4j_username: str
    neo4j_password: str

    text_index_name: str
    embedding_model_name: str
    llm_model_name: str
    llm_temperature: float

    @classmethod
    def from_env(cls) -> "GraphRAGConfig":
        return cls(
            vertex_ai_project_id=os.environ["VERTEX_AI_PROJECT_ID"],
            vertex_ai_location=os.getenv("VERTEX_AI_LOCATION", "us-central1"),
            vertex_ai_account_key_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),

            neo4j_uri=os.environ["NEO4J_URI"],
            neo4j_username=os.environ["NEO4J_USERNAME"],
            neo4j_password=os.environ["NEO4J_PASSWORD"],

            text_index_name=os.getenv("GRAPHRAG_TEXT_INDEX_NAME", "text_embeddings"),
            embedding_model_name=os.getenv("GRAPHRAG_EMBEDDING_MODEL", "text-embedding-004"),
            llm_model_name=os.getenv("GRAPHRAG_LLM_MODEL", "gemini-2.5-flash"),
            llm_temperature=float(os.getenv("GRAPHRAG_LLM_TEMPERATURE", "0.0")),
        )
