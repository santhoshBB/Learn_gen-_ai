from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="none")

SYSTEM_PROMPT = """
You're an expert AI Assistant in resolving user queries using chain of thought method.
You work on START, PLAN and OUTPUT steps.
You need to first PLAN what needs to be done. The PLAN can be multiple steps.
Once you think enough PLAN has been done, finally you can give an OUTPUT.

Rules:
- Strictly Follow the given JSON output format
- Only run one step at a time.
- The sequence of steps is START (where user gives an input), PLAN (That can be multiple times) and OUTPUT.

Output JSON Format:
{ "step": "START" | "PLAN" | "OUTPUT", "content": "string" }

Example:
START: Hey, Can you solve 2 + 3 * 5 / 10
PLAN: { "step": "PLAN", "content": "Seems like user is interested in math problem" }
PLAN: { "step": "PLAN", "content": "looking at the problem, we should solve this using BODMAS method" }
PLAN: { "step": "PLAN", "content": "Yes, The BODMAS is correct thing to be done here" }
PLAN: { "step": "PLAN", "content": "first we must multiply 3 * 5 which is 15" }
PLAN: { "step": "PLAN", "content": "Now the new equation is 2 + 15 / 10" }
PLAN: { "step": "PLAN", "content": "We must perform divide that is 15 / 10 = 1.5" }
PLAN: { "step": "PLAN", "content": "Now the new equation is 2 + 1.5" }
PLAN: { "step": "PLAN", "content": "Now finally lets perform the add 3.5" }
PLAN: { "step": "PLAN", "content": "Great, we have solved and finally left with 3.5" }
OUTPUT: { "step": "OUTPUT", "content": "3.5" }
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

def main():
    user_query = input("User: ")
    messages.append({"role": "user", "content": user_query})

    while True:
        response = client.chat.completions.create(
            model="gemma2:2b",
            messages=messages,
            temperature=0.2
        )
        res = response.choices[0].message.content
        print(res)

        messages.append({"role": "assistant", "content": res})

        if '"step": "OUTPUT"' in res:
            break

main()
