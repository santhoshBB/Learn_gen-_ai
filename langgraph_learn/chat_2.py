from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage

# LLM setup (you can keep using your gemma2:2b)
llm = ChatOllama(
    model="gemma2:2b",
    base_url="http://localhost:11434",
    temperature=0.7,
)

# State
class State(TypedDict):
    messages: Annotated[list, add_messages]
    mood: str           # We'll store the mood classification here


# ─── Nodes ────────────────────────────────────────────────────────────────

def ask_mood(state: State) -> dict:
    print("🤖 Hey there! How is your mood today?")
    print("(You can say: good / happy / great / bad / sad / tired / okay / etc)")
    user_input = input("Your mood: ").strip().lower()
    
    return {
        "messages": [HumanMessage(content=user_input)],
        "mood": user_input  # we'll use this for routing
    }


def happy_path(state: State) -> dict:
    msg = AIMessage(content="Yayy! That's awesome! ✨ What made you happy today? 😊")
    print("\n→ Happy vibe node")
    return {"messages": [msg]}


def sad_path(state: State) -> dict:
    msg = AIMessage(content="Aww... I'm sorry you're not feeling great today 😔\n"
                           "Want to talk about it? Or maybe I can tell you a bad joke? 🤗")
    print("\n→ Sad vibe node")
    return {"messages": [msg]}


def neutral_path(state: State) -> dict:
    msg = AIMessage(content="Okay cool, just vibing then 😎\n"
                           "What's on your mind today?")
    print("\n→ Neutral vibe node")
    return {"messages": [msg]}


# ─── Conditional Router ───────────────────────────────────────────────────

def decide_mood_route(state: State) -> Literal["happy", "sad", "neutral"]:
    """
    Simple keyword-based mood classifier
    You can make this smarter later using LLM if you want
    """
    mood_text = state["mood"].lower()
    print("Evaluating User Mood")
    happy_keywords = ["good", "great", "happy", "awesome", "nice", "excellent", "amazing", "yay"]
    sad_keywords = ["bad", "sad", "tired", "awful", "terrible", "depressed", "down", "not good"]

    if any(word in mood_text for word in happy_keywords):
        return "happy"
    
    elif any(word in mood_text for word in sad_keywords):
        return "sad"
    
    else:
        return "neutral"


# ─── Build Graph ──────────────────────────────────────────────────────────

workflow = StateGraph(State)

# Add nodes
workflow.add_node("ask_mood", ask_mood)
workflow.add_node("happy", happy_path)
workflow.add_node("sad", sad_path)
workflow.add_node("neutral", neutral_path)

# Edges
workflow.add_edge(START, "ask_mood")

# The magic part - conditional routing!
workflow.add_conditional_edges(
    "ask_mood",
    decide_mood_route,
    {
        "happy": "happy",
        "sad": "sad",
        "neutral": "neutral"
    }
)

# All paths end here (for this simple example)
workflow.add_edge("happy", END)
workflow.add_edge("sad", END)
workflow.add_edge("neutral", END)

# Compile
graph = workflow.compile()


# ─── Run the graph ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n User Mood Chat - Interactive LangGraph Example")
    
    # Start the graph
    result = graph.invoke({"messages": [], "mood": ""})
    
    print("\n" + "─"*60)
    print("Final conversation:")
    for msg in result["messages"]:
        if msg.content.strip():
            role = "You" if isinstance(msg, HumanMessage) else "Bot"
            print(f"{role}: {msg.content}")
    print("─"*60)