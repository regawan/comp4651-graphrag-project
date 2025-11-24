import asyncio

from backend.graphrag_config import GraphRAGConfig
from backend.graphrag_service import GraphRAGService
from dotenv import load_dotenv

load_dotenv()


async def main():
    config = GraphRAGConfig.from_env()
    service = GraphRAGService(config, True)

    # question = "How is precision medicine applied to Lupus? Provide the answer in list format."
    # answer = service.query(question)
    # print("Answer:\n", answer)

    service.delete_document(".pdf")

    documents = service.list_documents()
    print("Documents:\n", documents)

    files_to_add = ["../truncated-pdfs/biomolecules-11-00928-v2-trunc.pdf"]
    await service.build_knowledge_graph_from_pdfs(files_to_add)

    documents = service.list_documents()
    print("Documents:\n", documents)


if __name__ == "__main__":
    asyncio.run(main())

