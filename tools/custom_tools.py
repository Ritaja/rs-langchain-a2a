from langchain.tools import BaseTool
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
import duckdb
import os
from datetime import date


class InsuranceAnalyticsTool(BaseTool):
    """A tool for querying insurance data from DuckDB database using LLM-generated SQL."""

    name: str = "insurance_analytics"
    description: str = """
    Query insurance database to answer questions about customers, policies, and claims.
    This tool can execute SQL queries on the insurance database containing:
    - customers: customer information (customer_id, first_name, last_name, email, phone, date_of_birth, address, city, state, zip_code)
    - policies: insurance policies (policy_id, customer_id, policy_type, coverage_amount, premium_amount, start_date, end_date, status)
    - claims: insurance claims (claim_id, policy_id, claim_amount, claim_date, claim_status, claim_type, description)
    
    Input should be a natural language question about insurance data.
    Examples:
    - "How many customers do we have?"
    - "What is the total coverage amount for auto policies?"
    - "Show me all pending claims"
    - "Which customer has the highest claim amount?"
    - "What are the most common claim types?"
    """

    db_path: str = "insurance_data.db"
    llm: object  # LLM instance for SQL generation
    sql_prompt: object = None  # PromptTemplate for SQL generation

    def __init__(self, llm, **kwargs):
        # Create the SQL prompt template
        sql_prompt = PromptTemplate(
            input_variables=["question", "schema"],
            template="""You are a SQL expert. Given the following database schema and a natural language question, generate a SQL query to answer the question.

            Database Schema:
            {schema}

            Rules:
            1. Only use tables and columns that exist in the schema
            2. Use proper SQL syntax for DuckDB
            3. Use appropriate JOINs when data from multiple tables is needed
            4. For date comparisons, use DuckDB date functions like YEAR(), MONTH(), etc.
            5. Use COALESCE() for handling NULL values in aggregations
            6. Limit results to 20 rows unless specifically asked for more
            7. Use descriptive column aliases
            8. Return only the SQL query, no explanation

            Question: {question}

            SQL Query:"""
        )

        super().__init__(llm=llm, sql_prompt=sql_prompt, **kwargs)
        # Validate that LLM is provided
        if self.llm is None:
            raise ValueError("LLM is required for this tool")

    def _get_database_schema(self) -> str:
        """Get the database schema information."""
        return """
        Tables and Columns:

        1. customers
        - customer_id (INTEGER, PRIMARY KEY)
        - first_name (VARCHAR)
        - last_name (VARCHAR)
        - email (VARCHAR)
        - phone (VARCHAR)
        - date_of_birth (DATE)
        - address (VARCHAR)
        - city (VARCHAR)
        - state (VARCHAR)
        - zip_code (VARCHAR)

        2. policies
        - policy_id (INTEGER, PRIMARY KEY)
        - customer_id (INTEGER, FOREIGN KEY references customers.customer_id)
        - policy_type (VARCHAR) -- Values: 'auto', 'home', 'life', 'travel'
        - coverage_amount (DECIMAL)
        - premium_amount (DECIMAL)
        - start_date (DATE)
        - end_date (DATE)
        - status (VARCHAR) -- Values: 'active', 'expired', 'cancelled'

        3. claims
        - claim_id (INTEGER, PRIMARY KEY)
        - policy_id (INTEGER, FOREIGN KEY references policies.policy_id)
        - claim_amount (DECIMAL)
        - claim_date (DATE)
        - claim_status (VARCHAR) -- Values: 'pending', 'approved', 'denied'
        - claim_type (VARCHAR) -- Values: 'accident', 'theft', 'damage', 'medical', 'other'
        - description (TEXT)
        """

    def _convert_question_to_sql(self, question: str) -> str:
        """Convert natural language question to SQL query using LLM."""
        try:
            schema = self._get_database_schema()
            prompt = self.sql_prompt.format(question=question, schema=schema)

            if hasattr(self.llm, 'invoke'):
                # For ChatOpenAI
                response = self.llm.invoke([HumanMessage(content=prompt)])
                sql_query = response.content.strip()
            else:
                # For OpenAI
                sql_query = self.llm(prompt).strip()

            # Clean up the response (remove any markdown formatting)
            if sql_query.startswith('```sql'):
                sql_query = sql_query[6:]
            if sql_query.endswith('```'):
                sql_query = sql_query[:-3]
            sql_query = sql_query.strip()

            # Basic validation
            if not sql_query.upper().startswith('SELECT'):
                raise ValueError("Generated query is not a SELECT statement")

            return sql_query

        except Exception as e:
            raise Exception(f"Error generating SQL with LLM: {e}")

    def _run(self, query: str) -> str:
        """Execute the insurance analytics tool."""
        try:
            # Check if database file exists
            if not os.path.exists(self.db_path):
                return f"Database file '{self.db_path}' not found. Please run the data generation script first."

            # Connect to DuckDB
            conn = duckdb.connect(self.db_path)

            # Convert natural language to SQL
            sql_query = self._convert_question_to_sql(query)

            # Execute the query
            result = conn.execute(sql_query).fetchall()
            column_names = [desc[0] for desc in conn.description]

            # Format the results
            if not result:
                return "No data found for your query."

            # Create a formatted response
            response = f"Query: {query}\n"
            response += f"SQL: {sql_query.strip()}\n\n"
            response += "Results:\n"

            # Add column headers
            response += " | ".join(column_names) + "\n"
            response += "-" * (len(" | ".join(column_names))) + "\n"

            # Add data rows (limit to first 20 rows for readability)
            for i, row in enumerate(result[:20]):
                formatted_row = []
                for item in row:
                    if isinstance(item, (int, float)):
                        if isinstance(item, float):
                            formatted_row.append(f"{item:,.2f}")
                        else:
                            formatted_row.append(f"{item:,}")
                    elif isinstance(item, date):
                        formatted_row.append(item.strftime("%Y-%m-%d"))
                    else:
                        formatted_row.append(str(item))
                response += " | ".join(formatted_row) + "\n"

            if len(result) > 20:
                response += f"\n... showing first 20 of {len(result)} total results"

            conn.close()
            return response

        except Exception as e:
            return f"Error executing query: {str(e)}"

    async def _arun(self, query: str) -> str:
        """Async version of the insurance analytics tool."""
        return self._run(query)
