import neo4j
from neo4j_graphrag.llm import OpenAILLM as LLM
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings as Embeddings
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.generation.graphrag import GraphRAG

NEO4J_URI = ""
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "lDHDAAFTkU91TDH0echHMuVCch6KAgeBCqG0xdBsD-A"

neo4j_driver = neo4j.GraphDatabase.driver(NEO4J_URI,
                                          auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

ex_llm=LLM(
   model_name="gpt-4o-mini",
   model_params={
       "response_format": {"type": "json_object"},
       "temperature": 0
   })

embedder = Embeddings()

# 1. Build KG and Store in Neo4j Database
kg_builder_pdf = SimpleKGPipeline(
   llm=ex_llm,
   driver=neo4j_driver,
   embedder=embedder,
   from_pdf=True
)
await kg_builder_pdf.run_async(file_path='precision-med-for-lupus.pdf')

# 2. KG Retriever
vector_retriever = VectorRetriever(
   neo4j_driver,
   index_name="text_embeddings",
   embedder=embedder
)

# 3. GraphRAG Class
llm = LLM(model_name="gpt-4o")
rag = GraphRAG(llm=llm, retriever=vector_retriever)

# 4. Run
response = rag.search( "How is precision medicine applied to Lupus?")
print(response.answer)

#output
Precision medicine in systemic lupus erythematosus (SLE) is an evolving approach that aims to tailor treatment based on individual genetic, epigenetic, and pathophysiological characteristics…
