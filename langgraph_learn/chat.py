from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph


class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    return { "messages": ["Hi , this message is from chatbot"]}
    
def sample_node(state: State):
    return { "messages": ["Hi , this message is from sample node"]}

graph_builder = StateGraph(State)

graph_builder.add_node(chatbot, "chatbot")
graph_builder.add_node(sample_node, "sampleNode")