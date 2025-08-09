# Schema-Agnostic Pilot Training Retriever

This project implements a schema-agnostic retrieval system for pilot training records using a combination of LangChain, LangGraph, and FAISS. It allows for ingesting raw JSON data, performing complex natural language queries, and exporting structured data to Parquet files.

The system is designed to be "schema-agnostic" by leveraging Large Language Models (LLMs) to dynamically extract relevant information from unstructured JSON documents, eliminating the need for a predefined schema.

## Features

- **Dynamic Schema:** Extracts information from JSON records without requiring a fixed schema.
- **Natural Language Queries:** Uses LangGraph to parse natural language prompts into structured filters and queries.
- **Vector-Based Retrieval:** Employs FAISS for efficient similarity search on document embeddings.
- **Flexible Data Ingestion:** Ingests entire folders of JSON records.
- **Structured Export:** Exports query results to Apache Parquet format.
- **Deterministic Export:** Provides a direct export option based on metadata filters, bypassing the natural language processing pipeline.

## How It Works

The process is orchestrated by a LangGraph graph with three main nodes:

1.  **Parse Filters:** An LLM call parses the user's natural language prompt to extract key metadata filters (e.g., `airline`, `training_type`).
2.  **Retrieve:** A FAISS vector store retrieves the `TOP_K` most relevant documents based on the prompt. The retrieval is filtered by the metadata extracted in the previous step.
3.  **Extract:** For each candidate document, another LLM call (using function calling) extracts the required fields from the raw JSON content.

The final result is a structured dataset containing the extracted information, which can be displayed or saved as a Parquet file.

## Project Structure

```
.
├── app.py                  # Main CLI application entry point
├── data/                   # Default directory for data files
│   ├── airtransat/         # Sample data
│   └── virginair/          # Sample data
├── src/
│   ├── common/             # Shared modules (config, embeddings, etc.)
│   └── process/            # Core application logic
│       ├── graph.py        # LangGraph definition
│       ├── ingest.py       # Data ingestion logic
│       └── run.py          # Query execution logic
├── .env.example            # Example environment variables file
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Setup

### 1. Prerequisites

- Python 3.11+
- `uv` (for environment and package management)

### 2. Installation

Clone the repository and install the required dependencies using `uv`.

```bash
git clone <repository-url>
cd <repository-name>
uv pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the project root by copying the `.env.example` file.

```bash
cp .env.example .env
```

Update the `.env` file with your specific configurations, especially your OpenAI API key and base URL.

**Required Variables:**

- `OPENAI_API_KEY`: Your API key for OpenAI services.
- `BASE_URL`: The base URL for the OpenAI API.
- `CHAT_MODEL` (optional, defaults to `gpt-4o-mini`): The model to use for chat-based extraction and parsing.
- `EMBED_MODEL` (optional, defaults to `text-embedding-small`): The model to use for creating document embeddings.

## Usage

The application provides three main commands: `ingest`, `query`, and `export`.

### 0. Test

Run `uv run python document_generator.py` to generate mock data

### 1. Ingest Data

Before running any queries, you must ingest your data. This command processes all `.json` files in the specified folders, creates embeddings, and builds a FAISS index.

```bash
uv run python app.py ingest <folder1> <folder2> ...
```

**Example:**

```bash
uv run python app.py ingest ./data/airtransat ./data/virginair
```

This will create a `faiss_index` and a `manifest.parquet` file in the `data/` directory.

### 2. Query with Natural Language

Use the `query` command to ask questions in natural language. The `--out` flag is optional and will save the results to a Parquet file if provided.

```bash
uv run python app.py query "<your-prompt>" --out <output-path.parquet>
```

**Examples:**

- **To display results in the console:**
  ```bash
  uv run python app.py query "Which pilot from Air Transat had the most flight training hours on the A321?"
  ```

- **To export results to a Parquet file:**
  ```bash
  uv run python app.py query "Give me all the detail information about flight training for AirTransat pilots on the A330 that have a duration of more than 2 hours." --out airtransat_long_flights.parquet
  ```

### 3. Direct Export

The `export` command allows for deterministic, filter-based extraction without natural language processing. This is faster and more reliable for simple, known filters.

```bash
uv run python app.py export --airline "<airline-name>" --training-type "<training-type>" --out <output-path.parquet>
```

**Example:**

```bash
uv run python app.py export --airline "AirTransat" --training-type "Flight Training" --out direct_export.parquet
```
