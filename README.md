# GraphRAG using Neo4j

## Model provider: Google Vertex AI

To use and authenticate model:

`pip install neo4j_graphrag[google]`  
`export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"`


## Run with docker
1. Download the secret files `.env` and `plexiform-notch-478113-d0-0c739ffa1a72.json` from our
   secure file storage and add them to the highest project level.
2. Open the `docker-compose.yml` file and adjust the volume definition to point to the secret `.json` file.
3. Build the container: `docker compose build`
4. Start the container: `docker compose up`
5. Open `localhost:8000/docs` in your browser to discover the swagger UI (showcasing all endpoints)