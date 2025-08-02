#!/usr/bin/env python3
"""
A2A Server for Insurance Analytics Tool

This script starts an A2A-compatible server that exposes the InsuranceAnalyticsTool
wrapped in a LangChain agent, making it available via the A2A protocol.
"""
import argparse
from python_a2a import run_server, A2AServer, AgentCard, AgentSkill  # type: ignore
from langchain.agents import create_react_agent, AgentExecutor  # type: ignore
from langchain import hub  # type: ignore

from tools.custom_tools import InsuranceAnalyticsTool
from utils.azure_config import get_azure_llm
from utils.langfuse_config import get_langfuse_handler


def start_a2a_agent(db_path: str, host: str, port: int):
    """Start an A2A server exposing the Insurance LangChain agent"""
    llm = get_azure_llm()
    tools = [InsuranceAnalyticsTool(llm=llm, db_path=db_path)]
    prompt = hub.pull("hwchase17/react")
    # Initialize Langfuse handler for tracing
    langfuse_handler = get_langfuse_handler()
    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )

    # Define A2A agent metadata
    card = AgentCard(
        name="Insurance Analyst",
        description="Analyze insurance data with natural language queries",
        url=f"http://{host}:{port}",
        version="1.0.0",
        skills=[AgentSkill(
            name="insurance_query",
            description="Answer insurance data questions",
            examples=["How many customers?", "Show pending claims"]
        )]
    )

    # Wrap executor in A2A server
    class InsuranceAgentServer(A2AServer):
        def __init__(self):
            super().__init__(agent_card=card)
            self.executor = executor

        def handle_message(self, message):
            # A2A Message has content attribute for the user query
            # Invoke the agent, including Langfuse callback if available
            if langfuse_handler:
                result = self.executor.invoke(
                    {"input": message.content},
                    config={"callbacks": [langfuse_handler]}
                )
            else:
                result = self.executor.invoke({"input": message.content})
            return {"output": result.get("output")}

    server = InsuranceAgentServer()
    run_server(server, host=host, port=port)


def main():
    parser = argparse.ArgumentParser(
        description="Start A2A server for the Insurance Analytics Agent"
    )
    parser.add_argument(
        '--db-path', default='insurance_data.db',
        help="Path to DuckDB database file (default: insurance_data.db)"
    )
    parser.add_argument(
        '--host', default='0.0.0.0',
        help="Host to bind the A2A server (default: 0.0.0.0)"
    )
    parser.add_argument(
        '--port', type=int, default=5050,
        help="Port to run the A2A server (default: 5050)"
    )
    args = parser.parse_args()

    print(f"🔧 Starting A2A server on {args.host}:{args.port}")
    start_a2a_agent(args.db_path, args.host, args.port)


if __name__ == '__main__':
    main()
