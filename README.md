# GraphRAG using Neo4j

## Model provider: Google Vertex AI

To use and authenticate model:

`pip install neo4j_graphrag[google]`  
`export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"`

## Setup

### Run with docker
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


## Usage
Start the container as described in the setup section and open `localhost:8000/docs` in your browser
to access the SwaggerUI. Note: all endpoints listed in the SwaggerUI can be accessed via HTTP requests
from any browser or tools like Postman.

### Document Management
- **List Documents**: Simply run the request `GET /graphrag/docs` in the SwaggerUI or open `localhost:8000/graphrag/docs`
  in your browser to get a list with all indexed documents. The result looks like:
   ```
  {
    "docs": [
      {
        "document_id": "biomolecules-11-00928-v2-trunc.pdf",
        "chunks": 12
      },
      {
        "document_id": "GAP-between-patients-and-clinicians_2023_Best-Practice-trunc.pdf",
        "chunks": 11
      }
    ]
  }
   ```
- **Add new documents**: Open the `POST /graphrag/docs/add` endpoint in the SwaggerUI, select or drag&drop a file into the
  file selector filed and run the post request. The process of adding files is computational intensive and can take
  some time! The response should look like this:
   ```
  {
    "status": "ok",
    "ingested": [
      "biomolecules-11-00928-v2-trunc.pdf"
    ]
  }
  ```
  and the added file should be visible in the list documents response.
- **Remove a document**: Open the `DELETE /graphrag/docs/{id}` endpoint, insert the id of the document that should be
  removed and send the request. The response should look like:
  ```
  {
    "status": "deleted",
    "document_id": "biomolecules-11-00928-v2-trunc.pdf"
  }
  ```
  The deletion can be verified by rerunning the list documents endpoint.