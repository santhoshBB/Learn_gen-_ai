from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# LLM setup
llm = ChatOllama(
    model="gemma2:2b",
    base_url="http://localhost:11434",
    temperature=0.7,
)

# Very simple state (only conversation messages)
class State(dict):
    messages: list = add_messages

# Single node: just call LLM with full message history
def chat(state):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Build minimal graph
workflow = StateGraph(State)
workflow.add_node("chat", chat)
workflow.add_edge(START, "chat")
workflow.add_edge("chat", END)

print("=== Simple persistent chat (MongoDB) ===")
print("   Type your message or 'quit' to exit\n")

# Using context manager style for MongoDBSaver
with MongoDBSaver.from_conn_string(
    connection_string="mongodb://localhost:27017",
    db_name="langchain",
    collection_name="checkpointers"
) as checkpointer:

    # Compile graph with checkpointer inside the context
    graph = workflow.compile(checkpointer=checkpointer)

    # Fixed thread/conversation ID (memory key)
    config = {"configurable": {"thread_id": "chat-2025-001"}}

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye! 👋")
            break

        if not user_input:
            continue

        # Run the graph with only the new user message
        # → previous messages are automatically loaded by checkpointer
        result = graph.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        )

        # Show the latest AI response
        ai_response = result["messages"][-1].content
        print("AI :", ai_response)
        print("-" * 60)

print("\nConversation memory is stored in MongoDB.")
print("Run the script again → it should remember previous messages!")