import neo4j
from neo4j_graphrag.llm import VertexAILLM
from vertexai.generative_models import GenerationConfig
from neo4j_graphrag.embeddings import VertexAIEmbeddings
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.retrievers import VectorCypherRetriever
from neo4j_graphrag.generation.graphrag import GraphRAG
import asyncio

NEO4J_URI = "neo4j+s://cb673ac6.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "lDHDAAFTkU91TDH0echHMuVCch6KAgeBCqG0xdBsD-A"

neo4j_driver = neo4j.GraphDatabase.driver(NEO4J_URI,
                                          auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

generation_config = GenerationConfig(temperature=0.0)

ex_llm= VertexAILLM(
   model_name="gemini-2.5-flash",
   generation_config=generation_config
)

embedder = VertexAIEmbeddings(model='text-embedding-004', rate_limit_handler=None)

# 1. Build KG and Store in Neo4j Database
'''kg_builder = SimpleKGPipeline(
   llm=ex_llm,
   driver=neo4j_driver,
   embedder=embedder,
   from_pdf=True
)'''

pdf_file_paths = ['truncated-pdfs/biomolecules-11-00928-v2-trunc.pdf', 
                'truncated-pdfs/GAP-between-patients-and-clinicians_2023_Best-Practice-trunc.pdf', 
                'truncated-pdfs/pgpm-13-39-trunc.pdf', 
                'truncated-pdfs/nihms-362971-trunc.pdf']

# 3. GraphRAG Class
llm = VertexAILLM(
    model_name="gemini-2.5-flash", generation_config=generation_config
)

q = "How is precision medicine applied to Lupus? provide in list format."

async def main():
    # Ensures the text_embeddings vector index exists before inserting or querying data.
    '''await kg_builder.ensure_vector_index("text_embeddings", dimension=768)

    for path in pdf_file_paths:
        print(f"Processing : {path}")
        pdf_result = await kg_builder.run_async(file_path=path)
        print(f"Result: {pdf_result}")'''

    # 2. KG Retriever
    vc_retriever = VectorCypherRetriever(
        neo4j_driver,
        index_name="text_embeddings",
        embedder=embedder,
        retrieval_query="""
        //1) Go out 2-3 hops in the entity graph and get relationships
        WITH node AS chunk
        MATCH (chunk)<-[:FROM_CHUNK]-()-[relList:!FROM_CHUNK]-{1,2}()
        UNWIND relList AS rel

        //2) collect relationships and text chunks
        WITH collect(DISTINCT chunk) AS chunks,
        collect(DISTINCT rel) AS rels

        //3) format and return context
        RETURN '=== text ===n' + apoc.text.join([c in chunks | c.text], 'n---n') + 'nn=== kg_rels ===n' +
        apoc.text.join([r in rels | startNode(r).name + ' - ' + type(r) + '(' + coalesce(r.details, '') + ')' +  ' -> ' + endNode(r).name ], 'n---n') AS info
        """
    )

    rag = GraphRAG(llm=llm, retriever=vc_retriever)

    print(f"Vector + Cypher Response: \n{rag.search(q, retriever_config={'top_k':5}).answer}")

if __name__ == "__main__":
    asyncio.run(main())

