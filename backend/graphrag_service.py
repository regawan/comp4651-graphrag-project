from pathlib import Path

import neo4j
import vertexai
from google.oauth2 import service_account
from neo4j_graphrag.embeddings import VertexAIEmbeddings
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.llm import VertexAILLM
from neo4j_graphrag.retrievers import VectorCypherRetriever
from vertexai.generative_models import GenerationConfig
from backend.graphrag_config import GraphRAGConfig


class GraphRAGService:
    """
    High-level GraphRAG service. Provides the following methods:
    - __init__(config: GraphRAGConfig)
    - async build_knowledge_graph_from_pdfs(pdf_file_paths: list[str])
    - query(question: str, top_k: int = 5) -> str
    - list_documents(limit: int = 100)
    - delete_document(document_id: str)

    Can be used as follows:
        | config = GraphRAGConfig.from_env()
        | graphrag = GraphRAGService(config)
        | answer = graphrag.query("<Question>")
    """

    def __init__(self, config: GraphRAGConfig) -> None:
        self.config = config

        # Vertex AI setup: initialize client with credentials
        creds = service_account.Credentials.from_service_account_file(
            self.config.vertex_ai_account_key_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        vertexai.init(
            project=self.config.vertex_ai_project_id,
            location=self.config.vertex_ai_location,
            credentials=creds,
        )

        # Define the Neo4j driver
        self.neo4j_driver = neo4j.GraphDatabase.driver(
            self.config.neo4j_uri,
            auth=(self.config.neo4j_username, self.config.neo4j_password),
        )

        # Generation config, LLM and Embeddings setup
        generation_config = GenerationConfig(
            temperature=self.config.llm_temperature
        )

        self.llm = VertexAILLM(
            model_name=self.config.llm_model_name,
            generation_config=generation_config,
        )

        self.embedder = VertexAIEmbeddings(
            model=self.config.embedding_model_name,
            rate_limit_handler=None,
        )

        # Knowledge graph builder
        self.kg_builder = SimpleKGPipeline(
            llm=self.llm,
            driver=self.neo4j_driver,
            embedder=self.embedder,
            from_pdf=True,
        )

        # Create retriever and define final RAG object
        self.retriever = self._create_vector_cypher_retriever()
        self.rag = GraphRAG(llm=self.llm, retriever=self.retriever)


    def _create_vector_cypher_retriever(self) -> VectorCypherRetriever:
        """
        Private helper method to create a VectorCypherRetriever that:
        - uses the text embedding index,
        - walks the graph 1–2 hops out from retrieved chunks,
        - returns a combined text + KG-relations context string.
        """
        retrieval_query = """
        // 1) Go out 1–2 hops in the entity graph and get relationships
        WITH node AS chunk
        MATCH (chunk)<-[:FROM_CHUNK]-()-[relList:!FROM_CHUNK]-{1,2}()
        UNWIND relList AS rel

        // 2) collect relationships and text chunks
        WITH collect(DISTINCT chunk) AS chunks,
             collect(DISTINCT rel)   AS rels

        // 3) format and return context
        RETURN '=== text ===\n' +
               apoc.text.join([c IN chunks | c.text], '\n---\n') +
               '\n\n=== kg_rels ===\n' +
               apoc.text.join(
                    [r IN rels |
                        startNode(r).name + ' - ' + type(r) +
                        '(' + coalesce(r.details, '') + ')' +
                        ' -> ' + endNode(r).name
                    ],
                    '\n---\n'
               ) AS info
        """

        return VectorCypherRetriever(
            self.neo4j_driver,
            index_name=self.config.text_index_name,
            embedder=self.embedder,
            retrieval_query=retrieval_query,
        )


    async def build_knowledge_graph_from_pdfs(self, pdf_file_paths: list[str], embedding_dimension: int = 768) -> None:
        """
        Run the KG builder pipeline with a list of PDFs and store the resulting graph in Neo4j.
        """
        # Ensure the vector index exists
        self._ensure_vector_index(embedding_dimension)

        for path in pdf_file_paths:
            doc_id = Path(path).name

            if self._document_exists(doc_id):
                print(f"Skipping already ingested document: {doc_id}")
                continue

            print(f"Processing PDF: {path} (doc_id={doc_id})")
            result = await self.kg_builder.run_async(file_path=path, document_metadata={"source_id": doc_id})
            print(f"KG builder result for {path}: {result}")


    def _ensure_vector_index(self, dimension: int = 768):
        """
        Ensure the Neo4j vector index for Chunk embeddings exists. Run this once before ingesting PDFs.
        """
        with self.neo4j_driver.session() as session:
            session.run(
                """
                CREATE VECTOR INDEX text_embeddings IF NOT EXISTS
                FOR (c:Chunk) ON (c.embedding)
                OPTIONS {
                  indexConfig: {
                    `vector.dimensions`: $dim,
                    `vector.similarity_function`: 'cosine'
                  }
                }
                """,
                dim=dimension,
            )


    def _document_exists(self, doc_id: str) -> bool:
        """
        Return True if a Document with this id (source_id or path) exists.
        """
        query = """
        MATCH (d:Document)
        WHERE d.source_id = $doc_id OR d.path = $doc_id
        RETURN COUNT(d) > 0 AS exists
        """
        with self.neo4j_driver.session() as session:
            record = session.run(query, doc_id=doc_id).single()
            return bool(record["exists"])


    def query(self, question: str, top_k: int = 5) -> str:
        """
        Run a GraphRAG query and return the answer text.

        This is sync to be easy to call from typical REST handlers.
        If your framework is async (FastAPI), you can run it in a
        thread pool via `run_in_executor`.
        """
        result = self.rag.search(
            question,
            retriever_config={"top_k": top_k},
        )
        return result.answer


    def list_documents(self, limit: int = 100):
        """
        Return a list of indexed documents with basic stats.
        """
        query = """
        MATCH (d:Document)<-[:FROM_DOCUMENT]-(c:Chunk)
        WITH coalesce(d.source_id, d.path) AS doc, count(c) AS chunks
        RETURN doc AS document_id, chunks
        ORDER BY chunks DESC
        LIMIT $limit
        """
        with self.neo4j_driver.session() as session:
            result = session.run(query, limit=limit)
            return [record.data() for record in result]


    def delete_document(self, document_id: str):
        with self.neo4j_driver.session() as session:
            # Delete all chunks and related KG nodes/edges of a document
            session.run(
                """
                MATCH (d:Document)
                WHERE d.source_id = $doc OR d.path = $doc
                OPTIONAL MATCH (d)<-[:FROM_DOCUMENT]-(c:Chunk)
                DETACH DELETE c, d
                """,
                doc=document_id,
            )
            # Cleans up orphan entity nodes (if available)
            session.run("""
                MATCH (e:Entity)
                WHERE NOT (e)--()
                DELETE e
            """)
