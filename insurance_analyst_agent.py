#!/usr/bin/env python
"""
Insurance Analyst Agent with DuckDB Integration and Langfuse Tracing

This script creates an intelligent agent that can analyze insurance data
stored in a DuckDB database and answer natural language questions about
customers, policies, and claims. It includes Langfuse for observability
and tracing of agent interactions.
"""

import argparse
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from utils.azure_config import get_azure_llm
from utils.langfuse_config import get_langfuse_handler
from tools.custom_tools import InsuranceAnalyticsTool


def create_insurance_agent(db_path: str = "insurance_data.db"):
    """Create an insurance analyst agent with DuckDB analytics capabilities."""

    # Initialize the Azure OpenAI LLM
    llm = get_azure_llm()

    # Create the insurance analytics tool
    insurance_tool = InsuranceAnalyticsTool(db_path=db_path, llm=llm)

    # Create tools list
    tools = [insurance_tool]

    # Get the ReAct prompt from hub
    prompt = hub.pull("hwchase17/react")

    # Initialize Langfuse handler for tracing and integrate into agent
    langfuse_handler = get_langfuse_handler()
    if langfuse_handler:
        # Create the agent with Langfuse callback handler
        agent = create_react_agent(
            llm,
            tools,
            prompt
        )
        callbacks = [langfuse_handler]
    else:
        # Create the agent without Langfuse
        agent = create_react_agent(llm, tools, prompt)
        callbacks = []

    # Create agent executor with (optional) Langfuse tracing
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )

    return agent_executor


def interactive_chat(agent_executor):
    """Start an interactive chat session with the insurance agent."""
    print("\n" + "="*60)
    print("🏛️  INSURANCE ANALYST AGENT")
    print("="*60)
    print("Ask me anything about your insurance data!")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("-" * 60)

    # Initialize Langfuse handler for tracing and integrate into agent
    langfuse_handler = get_langfuse_handler()

    # Show available query examples
    print("\n📊 Example questions you can ask:")
    examples = [
        "How many customers do we have?",
        "What is the total coverage amount for auto policies?",
        "Show me all pending claims",
        "Which customer has the highest claim amount?",
        "What are the most common claim types?",
        "What is our profit analysis by policy type?",
        "Show me the loss ratio for each policy type",
        "Who are the customers with the most policies?",
        "How many claims were filed this year?",
        "What is the average premium by policy type?"
    ]

    for i, example in enumerate(examples, 1):
        print(f"  {i:2d}. {example}")

    print("\n" + "-" * 60)

    while True:
        try:
            # Get user input
            user_input = input("\n🔍 Your question: ").strip()

            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Thank you for using Insurance Analyst Agent!")
                break

            if not user_input:
                print("Please enter a question about the insurance data.")
                continue

            # Process the query
            print(f"\n🤔 Analyzing: {user_input}")
            print("-" * 40)

            try:
                response = agent_executor.invoke(
                    {"input": user_input},
                    config={
                        "callbacks": [langfuse_handler]
                    }
                )
                print(f"\n💡 Answer:\n{response['output']}")
            except Exception as e:
                print(f"\n❌ Error processing your question: {str(e)}")
                print(
                    "Please try rephrasing your question or ask something else."  # noqa: E501
                )

            print("\n" + "="*60)

        except KeyboardInterrupt:
            print("\n\n👋 Thank you for using Insurance Analyst Agent!")
            break
        except EOFError:
            print("\n\n👋 Thank you for using Insurance Analyst Agent!")
            break


def demo_queries(agent_executor):
    """Run a demo with predefined queries."""
    print("\n" + "="*60)
    print("🚀 INSURANCE ANALYST AGENT - DEMO MODE")
    print("="*60)

    # Initialize Langfuse handler for tracing and integrate into agent
    langfuse_handler = get_langfuse_handler()

    demo_questions = [
        "How many customers do we have?",
        "What is the total coverage amount by policy type?",
        "Show me all pending claims",
        "What is our profit analysis by policy type?",
        "Who are the top 5 customers with the highest premiums?"
    ]

    for i, question in enumerate(demo_questions, 1):
        print(f"\n📊 Demo Query {i}: {question}")
        print("-" * 50)

        try:
            response = agent_executor.invoke(
                {"input": question},
                config={
                    "callbacks": [langfuse_handler]
                }
            )
            print(f"Answer: {response['output']}")
        except Exception as e:
            print(f"Error: {str(e)}")

        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description=(
            'Insurance Analyst Agent with DuckDB Integration '
            'and Langfuse Tracing'
        )
    )
    parser.add_argument(
        '--db-path',
        default='insurance_data.db',
        help=(
            'Path to DuckDB database file '
            '(default: insurance_data.db)'
        )
    )
    parser.add_argument(
        '--mode',
        choices=['interactive', 'demo'],
        default='interactive',
        help=(
            'Run mode: interactive chat or demo queries '
            '(default: interactive)'
        )
    )

    args = parser.parse_args()

    try:
        # Create the insurance agent
        print("🔧 Initializing Insurance Analyst Agent...")
        agent_executor = create_insurance_agent(args.db_path)
        print("✅ Agent initialized successfully!")

        # Run in specified mode
        if args.mode == 'demo':
            demo_queries(agent_executor)
        else:
            interactive_chat(agent_executor)

    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        print("\nMake sure you have:")
        print("1. Set up your Azure OpenAI environment variables")
        print("2. Generated insurance data using generate_synthetic_data.py")
        print("3. Installed all required dependencies")
        print("4. (Optional) Set up Langfuse keys for tracing")


if __name__ == "__main__":
    main()
