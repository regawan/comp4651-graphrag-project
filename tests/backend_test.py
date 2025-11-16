from backend.graphrag_config import GraphRAGConfig
from backend.graphrag_service import GraphRAGService
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    config = GraphRAGConfig.from_env()
    service = GraphRAGService(config)

    question = "How is precision medicine applied to Lupus? Provide the answer in list format."
    answer = service.query(question)
    print("Answer:\n", answer)

    documents = service.list_documents()
    print("Documents:\n", documents)