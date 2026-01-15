from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="gemma2:2b",           # make sure you ran: ollama pull gemma2:2b
    base_url="http://localhost:11434",
    temperature=0.7,
    # num_ctx=8192,             # optional - increase if needed
)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    print("from chatbot node")
    response = llm.invoke(state["messages"])   # ← ChatOllama expects message list
    return {"messages": [response]}
    
def sample_node(state: State):
    print('\n\nThis is inseide sample NODe')
    return { "messages": ["Hi , this message is from sample node"]}

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("sampleNode", sample_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot","sampleNode")
graph_builder.add_edge("sampleNode",END)


graph= graph_builder.compile()

updated_state= graph.invoke(State({"messages":["Hi this is santhosh"]}))
print("\n\nUpdated State", updated_state)
