# Insurance Analyst Agent

[![LangChain](https://img.shields.io/badge/langchain-00B9FF?style=flat&logo=langchain&logoColor=white)](https://github.com/hwchase17/langchain) [![DuckDB](https://img.shields.io/badge/DuckDB-FFD93D?style=flat&logo=duckdb&logoColor=black)](https://duckdb.org/) [![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-0078D4?style=flat&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/services/openai/) [![Langfuse](https://img.shields.io/badge/langfuse-292929?style=flat&logo=langfuse&logoColor=white)](https://langfuse.com/)

This repository showcases A2A agents using the OSS tools mentioned above.

An intelligent insurance analytics tool built with LangChain, DuckDB, and Azure OpenAI, featuring observability with Langfuse and A2A protocol support.

## Features

- Generate synthetic insurance data (customers, policies, claims) using `faker` and `duckdb`.
- Interactive CLI agent for natural language queries about insurance data.
- Demo mode for running predefined analytics queries.
- A2A-compatible server exposing the agent via HTTP and a corresponding client for integration.
- Observability and tracing through Langfuse.

## Prerequisites

- Linux / macOS / Windows with WSL (Python 3.9+).
- Docker and Docker Compose (for Langfuse, PostgreSQL, ClickHouse services).
- Azure OpenAI resource:
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_DEPLOYMENT_NAME`
  - (Optional) `AZURE_OPENAI_API_VERSION`
- Langfuse account (if using observability):
  - `LANGFUSE_API_KEY`
  - `LANGFUSE_API_URL` (if custom)
- A `.env` file in the root directory containing the above environment variables.

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url> insurance-analyst-agent
   cd insurance-analyst-agent
   ```
2. Initialize Python environment and install dependencies:
   ```bash
   ./startup.sh
   ```
3. (Optional) Start Langfuse and database services:
   ```bash
   docker compose up -d
   ```
4. Generate synthetic data:
   ```bash
   python generate_synthetic_data.py --db-path insurance_data.db
   ```

## Usage

### Interactive Agent

Launch the CLI agent to ask custom questions:
```bash
python insurance_analyst_agent.py --mode interactive --db-path insurance_data.db
```

### Demo Mode

Run a series of predefined analytics queries:
```bash
python insurance_analyst_agent.py --mode demo --db-path insurance_data.db
```

### A2A Server & Client

1. Start the A2A server:
   ```bash
   python a2a_insurance_agent.py --host 0.0.0.0 --port 5050 --db-path insurance_data.db
   ```
2. In a separate terminal, run the client:
   ```bash
   python a2a_client.py --host localhost --port 5050
   ```
3. Type queries and receive JSON-over-HTTP responses.

## Custom Tools

The `tools/custom_tools.py` module defines `InsuranceAnalyticsTool`, which encapsulates SQL queries against DuckDB and is registered with LangChain.

## Configuration

- Adjust database path with the `--db-path` flag.
- Control LLM temperature and model parameters via Azure environment variables.
- Enable or disable Langfuse tracing by installing `langfuse` and setting `LANGFUSE_API_KEY`.

## Development

- Linting: ESLint and standard Python linters available in the Dev Container.
- Virtual environment: `.venv` is used for Python dependencies.
- To stop services:
  ```bash
  docker compose down
  ```

## License

MIT License
