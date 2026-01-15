from openai import OpenAI
import requests

client = OpenAI(base_url="http://localhost:11434/v1", api_key="none")


def get_weather(city:str):
    url= f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return F"The wetaher is {response.text} in {city}"
    return "something went wrong"

def main():
    try:
        user_query = input(">")
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": user_query}],
            model="gemma2:2b"
        )
        print(f"🤖:{response.choices[0].message.content}")
    except KeyboardInterrupt:
        print("\n👋 Exiting...")

main()

