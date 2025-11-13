llm = LLM(model_name="gpt-4o",  model_params={"temperature": 0.0})

rag_template = RagTemplate(template='''Answer the Question using the following Context. Only respond with information mentioned in the Context. Do not inject any speculative information not mentioned. 

# Question:
{query_text}
 
# Context:
{context}

# Answer:
''', expected_inputs=['query_text', 'context'])

vector_rag  = GraphRAG(llm=llm, retriever=vector_retriever, prompt_template=rag_template)

graph_rag = GraphRAG(llm=llm, retriever=graph_retriever, prompt_template=rag_template)

q = "Can you summarize systemic lupus erythematosus (SLE)? including common effects, biomarkers, and treatments? Provide in detailed list format."

vector_rag.search(q, retriever_config={'top_k':5}).answer
graph_rag.search(q, retriever_config={'top_k':5}).answer
