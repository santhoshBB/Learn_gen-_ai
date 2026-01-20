# Ollamm not wokring with mem0

from mem0 import Memory
from openai import OpenAI

# ──── CONFIGURATION ────────────────────────────────────────────────

OLLAMA_API_BASE = "http://localhost:11434/v1"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "mem0_chat_2026"   # Change if you want fresh start

USER_ID = "santhosh_local"           # Your personal identifier
LLM_MODEL = "gemma2:2b"              # or "llama3.2:3b", etc.

# LLM client (OpenAI compatible)
llm_client = OpenAI(
    base_url=OLLAMA_API_BASE,
    api_key="ollama",                # dummy value - ignored by Ollama
)

# ──── MEM0 CONFIGURATION ───────────────────────────────────────────

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QDRANT_HOST,
            "port": QDRANT_PORT,
            "collection_name": COLLECTION_NAME,
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text"     # ← this is the correct & minimal config
            # NO base_url, NO ollama_base_url here in current versions!
        }
    },
    "llm": {
        "provider": "openai",               # ← we use openai-compatible endpoint
        "config": {
            "model": LLM_MODEL,
            "api_key": "ollama",
            "base_url": OLLAMA_API_BASE,
            "temperature": 0.75,
        }
    },
    # Optional but useful
    "version": "v1.1",
}

# ──── INITIALIZATION ───────────────────────────────────────────────

print("Starting Mem0 initialization...")
print(f"  • LLM:        {LLM_MODEL} @ Ollama")
print("  • Embeddings: nomic-embed-text")
print(f"  • Vector DB:  Qdrant @ {QDRANT_HOST}:{QDRANT_PORT}")
print(f"  • Collection: {COLLECTION_NAME}")
print("-" * 70)

memory = Memory.from_config(config)

print("Mem0 initialized successfully ✓\n")

# ──── CHAT LOOP ────────────────────────────────────────────────────

print("Chat ready! (type exit / quit / bye to finish)\n")

while True:
    try:
        user_input = input("You: ").strip()

        if user_input.lower() in {"exit", "quit", "bye", "q"}:
            print("\nGoodbye! 👋\n")
            break

        if not user_input:
            continue

        # Retrieve relevant memories
        memories = memory.search(
            query=user_input,
            user_id=USER_ID,
            limit=5
        )

        memory_text = "\n".join(f"• {m.memory.strip()}" for m in memories) if memories else "(no relevant memories found)"

        system_prompt = f"""You are a helpful, concise and friendly assistant.
You remember important things about the user from previous conversations.

Relevant memories:
{memory_text}

Answer naturally."""

        # Generate response
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.75,
            max_tokens=1400,
        )

        answer = response.choices[0].message.content.strip()

        print("\nAI  :", answer)
        print("-" * 70)

        # Save the conversation turn
        memory.add(
            messages=[
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": answer}
            ],
            user_id=USER_ID
        )

    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
        break
    except Exception as e:
        print(f"\nError: {str(e)}\nContinuing anyway...\n")