from dotenv import load_dotenv
from mem0 import Memory
import os
from openai import OpenAI
import json
load_dotenv()


client = OpenAI()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

config ={
    "version":"v1.1",
    "embedder":{
        "provider": "openai",
        "config":{ "api_key": OPENAI_API_KEY, "model":"text-embedding-3-small"}
    },
    "llm":{
        "provider": "openai",
        "config":{ "api_key": OPENAI_API_KEY, "model":"gpt-4o-mini"}
    },
    "vector_store":{
        "provider": "qdrant",
        "config":{
            "host": "locahost",
            "port":"6333"
        }
    },
    
}

mem_client = Memory.from_config(config)

while True:

    user_query=input("> ")
    # gives only the relevant memory
    search_memory= mem_client.search(query=user_query, user_id='some_random_id_001')

    memories =[
        f"ID: {mem.get("id")}\nMemory: {mem.get("memmory")}" for mem in search_memory.get("results")
    ]

    SYSTEM_PROMPT=f"""
    Here is the context about the user:
    {json.dumps(memories)}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ]
    )

    ai_response =response.choices[0].message.content
    print(ai_response)
    mem_client.add(
        user_id="some_random_id_001",
        messages=[
            {"role": "user", "content": user_query},
        {"role": "assistant", "content": ai_response}
        ]
        
    )