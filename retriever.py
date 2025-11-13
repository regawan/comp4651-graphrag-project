from neo4j_graphrag.retrievers import VectorCypherRetriever

graph_retriever = VectorCypherRetriever(
    driver,
    index_name="text_embeddings",
    embedder=embedder,
    retrieval_query="""
//1) Go out 2-3 hops in the entity graph and get relationships
WITH node AS chunk
MATCH (chunk)<-[:FROM_CHUNK]-(entity)-[relList:!FROM_CHUNK]-{1,2}(nb)
UNWIND relList AS rel

//2) collect relationships and text chunks
WITH collect(DISTINCT chunk) AS chunks, collect(DISTINCT rel) AS rels

//3) format and return context
RETURN apoc.text.join([c in chunks | c.text], '\n') + 
  apoc.text.join([r in rels | 
  startNode(r).name+' - '+type(r)+' '+r.details+' -> '+endNode(r).name],  
  '\n') AS info
"""
)
