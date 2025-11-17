# GraphRAG using Neo4j

## Model provider: Google Vertex AI

To use and authenticate model:

`pip install neo4j_graphrag[google]`  
`export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"`


## Run with docker
1. Clone this repository.
2. Download the secret files `.env` and `plexiform-notch-478113-d0-0c739ffa1a72.json` from our
   secure file storage and add them to the highest project level.
3. Open the `docker-compose.yml` file and adjust the volume definition to point to the secret `.json` file
   ```
   volumes:
      - <INSERT ABSOLUTE PATH TO JSON>:/secrets/vertex-ai-service-account.json:ro
   ```
4. Build the container: `docker compose build`
5. Start the container: `docker compose up`
6. Open `localhost:8000/docs` in your browser to discover the swagger UI (showcasing all endpoints)
7. After running stop the container: `docker compose stop`