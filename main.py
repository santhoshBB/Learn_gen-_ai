from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="none")

response = client.chat.completions.create(
    model="gemma2:2b",
    messages=[
        {"role": "user", "content": "Hello from Santhosh!"}
    ]
)

print(response.choices[0].message.content)
