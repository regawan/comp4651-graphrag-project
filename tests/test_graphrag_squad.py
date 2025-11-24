"""
Benchmark script for GraphRAG vs standard RAG using SQuAD dataset,
using Hugging Face evaluate library for EM and F1.
"""

import asyncio
import time
from datasets import load_dataset
import evaluate
from backend.graphrag_service import GraphRAGService
from neo4j_graphrag.retrievers import VectorRetriever
from backend.graphrag_config import GraphRAGConfig
from dotenv import load_dotenv

load_dotenv()


def benchmark_rag(rag_service, dataset, top_k=5):
    squad_metric = evaluate.load("squad")
    predictions = []
    references = []
    latencies = []

    for i, item in enumerate(dataset):
        question = item["question"]
        answers = item["answers"]["text"]

        # Measure latency per query
        start_time = time.time()
        pred_text = rag_service.query(question, top_k=top_k)
        latency = time.time() - start_time
        latencies.append(latency)

        # Prepare for evaluate
        predictions.append({"id": str(i), "prediction_text": pred_text})
        references.append(
            {
                "id": str(i),
                "answers": {"text": answers, "answer_start": [0] * len(answers)},
            }
        )

    # Compute SQuAD metric
    results = squad_metric.compute(predictions=predictions, references=references)

    # Average latency
    avg_latency = sum(latencies) / len(latencies)

    return results["exact_match"], results["f1"], avg_latency


async def main():
    # Load SQuAD subset (first 50 examples for speed)
    squad = load_dataset("squad")
    train_data = squad["train"][:50]

    # Convert to documents
    documents = []
    seen_texts = set()
    for i, item in enumerate(train_data):
        context = item["context"]
        if context not in seen_texts:
            seen_texts.add(context)
            documents.append({"doc_id": f"squad_{i}", "text": context})

    # Load GraphRAG config
    config = GraphRAGConfig.from_env()  # assumes env vars set
    print(f"Ingesting {len(documents)} SQuAD documents into KG...")

    # 1️⃣ GraphRAG ingestion
    graphrag_service = GraphRAGService(config, from_pdf=False)
    await graphrag_service.build_knowledge_graph_from_texts(documents)

    # 2️⃣ Benchmark GraphRAG
    print("Running GraphRAG benchmark...")
    em, f1, latency = benchmark_rag(graphrag_service, train_data)
    print(
        f"\nGraphRAG Results - EM: {em:.3f}, F1: {f1:.3f}, Latency: {latency:.3f}s per query"
    )

    # 3️⃣ Benchmark Standard RAG (vector retriever)
    class StandardRAGService(GraphRAGService):
        def _create_vector_cypher_retriever(self):
            return VectorRetriever(
                self.neo4j_driver,
                index_name=self.config.text_index_name,
                embedder=self.embedder,
            )

    standard_rag_service = StandardRAGService(config, from_pdf=False)
    print("Running Standard RAG benchmark...")
    em2, f1_2, latency2 = benchmark_rag(standard_rag_service, train_data)
    print(
        f"\nStandard RAG Results - EM: {em2:.3f}, F1: {f1_2:.3f}, Latency: {latency2:.3f}s per query"
    )


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
