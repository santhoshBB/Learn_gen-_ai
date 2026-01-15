from openai import OpenAI

# Connect to local Ollama server running Gemma 2B
client = OpenAI(base_url="http://localhost:11434/v1", api_key="none")

# --- Persona setting ---
persona = "You are a friendly and witty assistant who explains things in simple terms with humor."

# --- Prompt type selector ---
prompt_type = "cot"  # change to: zero-shot | one-shot | few-shot | cot

# Start messages with persona system message
messages = [
    {"role": "system", "content": persona}  # Persona instruction
]

# Append user prompt based on type
match prompt_type:
    # ZERO-SHOT
    case "zero-shot":
        messages.append(
            {"role": "user", "content": "Explain what recursion is in simple terms."}
        )

    # ONE-SHOT
    case "one-shot":
        messages.append(
            {"role": "user", "content":
                "Translate English to French.\n"
                "Example:\n"
                "English: Good morning\n"
                "French: Bonjour\n\n"
                "English: I like coding\n"
                "French:"
            }
        )

    # FEW-SHOT
    case "few-shot":
        messages.append(
            {"role": "user", "content":
                "Rewrite sentences in CAVEMAN style.\n"
                "Example:\n"
                "I am hungry → Me need food.\n"
                "You are my friend → You friend me.\n\n"
                "Sentence: I love programming →"
            }
        )

    # CHAIN OF THOUGHT (CoT)
    case "cot":
        messages.append(
            {"role": "user", "content":
                "Solve step by step:\n"
                "If Sam has 4 apples, buys 7 more, "
                "and gives away 3, how many apples remain?"
            }
        )

    # UNKNOWN OPTION FALLBACK
    case _:
        messages.append(
            {"role": "user", "content": "Hello from Santhosh! (default fallback)"}
        )

# Send the request
response = client.chat.completions.create(
    model="gemma2:2b",
    messages=messages
)

# Print model response
print("\n=== MODEL RESPONSE ===")
print(response.choices[0].message.content)
