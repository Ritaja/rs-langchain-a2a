#!/usr/bin/env python3
"""
A2A Client for Insurance Analytics Agent

This script connects to the A2A server and allows interactive querying of insurance data.
"""
import argparse
from python_a2a import A2AClient  # type: ignore
from python_a2a.models.message import Message, TextContent, MessageRole  # type: ignore


def main():
    parser = argparse.ArgumentParser(
        description="A2A client for Insurance Analytics Agent"
    )
    parser.add_argument(
        '--host', default='localhost',
        help="A2A server host (default: localhost)"
    )
    parser.add_argument(
        '--port', type=int, default=5050,
        help="A2A server port (default: 5050)"
    )
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"
    print(f"🔗 Connecting to A2A server at {url}")
    # Connect to the A2A server endpoint
    client = A2AClient(endpoint_url=url)

    print("\nType 'exit' or 'quit' to end.")
    while True:
        query = input("🗨️  Your question: ").strip()
        if not query or query.lower() in ['exit', 'quit', 'q', 'bye']:
            print("👋 Goodbye!")
            break
        try:
            # Send a Message object and get a Message response
            message = Message(content=TextContent(
                text=query), role=MessageRole.USER)
            response_msg = client.send_message(message)
            output = response_msg.content.text
            print(f"💡 Answer: {output}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == '__main__':
    main()
