from openai import OpenAI
import requests
import json

client = OpenAI(base_url="http://localhost:11434/v1", api_key="none")

def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather is {response.text.strip()} in {city}"
    return "something went wrong"

SYSTEM_PROMPT = """
You're an expert AI Assistant in resolving user queries using chain of thought method.
You work on START, PLAN, TOOL and OUTPUT steps.

RULES:
- Strictly Follow the JSON output format.
- Only run one step at a time.
- The sequence of steps always begins with START (where user gives an input), then PLAN (can be many times), optionally TOOL (if external function required) and finally OUTPUT.
- TOOL Step is used when you need to call a function.

Output JSON format:
{ "step": "START" | "PLAN" | "TOOL" | "OUTPUT", "content": "string" }

------------------------------------------------
Example 1 (Math):
START: Hey, Can you solve 2 + 3 * 5 / 10
PLAN: { "step": "PLAN", "content": "User wants to solve a math expression" }
PLAN: { "step": "PLAN", "content": "We apply BODMAS rule" }
PLAN: { "step": "PLAN", "content": "Multiply 3 * 5 = 15" }
PLAN: { "step": "PLAN", "content": "Divide 15 / 10 = 1.5" }
PLAN: { "step": "PLAN", "content": "Add 2 + 1.5 = 3.5" }
OUTPUT: { "step": "OUTPUT", "content": "Result is 3.5" }

------------------------------------------------
Example 2 (Weather):
START: What is the weather in Mumbai?
PLAN: { "step": "PLAN", "content": "User wants weather information" }
PLAN: { "step": "PLAN", "content": "We need to call the weather tool" }
TOOL: { "step": "TOOL", "content": "get_weather('mumbai')" }
PLAN: { "step": "PLAN", "content": "Received temperature and condition" }
OUTPUT: { "step": "OUTPUT", "content": "It's overcast 29°C in Mumbai" }
------------------------------------------------
"""

def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    user_query = input("> ")
    messages.append({"role": "user", "content": user_query})

    while True:
        resp = client.chat.completions.create(
            messages=messages,
            model="gemma2:2b",
            temperature=0.3
        )
        res = resp.choices[0].message.content
        print(res)

        messages.append({"role": "assistant", "content": res})

        # Check if tool step triggered
        try:
            data = json.loads(res)
            if data.get("step") == "TOOL":
                text = data["content"]
                city = text[text.find("(")+1:text.find(")")].replace("'", "").replace('"', "")
                tool_response = get_weather(city)
                print(f"🛠️ TOOL RESULT: {tool_response}")
                messages.append({"role": "user", "content": tool_response})
        except:
            pass

        # 👉 KEY FIX: ask AI to continue planning
        if '"step": "OUTPUT"' not in res:
            messages.append({"role": "user", "content": "continue in JSON"})

        if '"step": "OUTPUT"' in res:
            break

if __name__ == "__main__":
    main()
