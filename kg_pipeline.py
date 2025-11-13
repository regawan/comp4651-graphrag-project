driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

ex_llm=OpenAILLM(
    model_name="gpt-4o-mini",
    model_params={
        "response_format": {"type": "json_object"},
        "temperature": 0
    }
)
embedder = OpenAIEmbeddings()

node_labels = ["Anatomy", "BiologicalProcess", ...]
rel_types = ["ACTIVATES", "AFFECTS", "ASSESSES",..."TREATS", "USED_FOR"]

kg_builder_pdf = SimpleKGPipeline(
    llm=ex_llm,
    driver=driver,
    text_splitter=FixedSizeSplitter(chunk_size=500, chunk_overlap=100),
    embedder=embedder,
    entities=node_labels,
    relations=rel_types,
    prompt_template=prompt_template,
    from_pdf=True
)

pdf_file_paths = ['dataset', 'dataset2','dataset3']

for path in pdf_file_paths:
    graph_data = await kg_builder_pdf.run_async(file_path=path)
